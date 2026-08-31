#!/usr/bin/env ruby
# frozen_string_literal: true

# Generate Jekyll _posts entries from GitHub releases for the BJC-related
# repos listed in REPOS. Idempotent: existing post files are left alone, so
# the first run backfills and subsequent runs only add new releases.
#
# Usage:
#   ruby script/generate_release_news.rb [--dry-run] [--verbose]
#
# A GITHUB_TOKEN env var is recommended (raises the API rate limit from 60
# to 5000 requests/hour). In GitHub Actions the default token is enough.

require 'date'
require 'fileutils'
require 'json'
require 'net/http'
require 'optparse'
require 'uri'

REPOS = [
  { short_name: 'Snap*!*',           repo: 'jmoenig/Snap',         slug: 'snap' },
  { short_name: 'BJC Curriculum',    repo: 'bjc-edc/bjc-r',        slug: 'bjc-curriculum' },
  { short_name: 'Snap*!* Community', repo: 'snap-cloud/snapCloud', slug: 'snap-community' },
  { short_name: 'Snap*!* Manual',    repo: 'snap-cloud/manual',    slug: 'snap-manual' }
].freeze

POST_BODY_TEMPLATE = <<~MARKDOWN
  ---
  layout: post
  title: %{title}
  date: %{date}
  category: news
  tags: release, %{slug}
  source: %{url}
  ---

  %{intro}

  %{body}

  [View this release on GitHub](%{url})
MARKDOWN

POSTS_DIR = File.expand_path('../_posts', __dir__)

# Match titles that are purely timestamps. Version numbers like "1.2.3" must
# NOT match, so we require either an explicit date layout or a compact
# YYYYMMDD-style stamp.
TIMESTAMP_PATTERNS = [
  %r{\A\d{4}[-/.]\d{1,2}[-/.]\d{1,2}([\sT]\d{1,2}[:.\-]\d{1,2}([:.\-]\d{1,2})?Z?)?\z},
  /\A\d{8}([-T_]\d{4,6})?\z/,
  /\A\d{10,}\z/
].freeze

def slugify(string)
  string.to_s.downcase.gsub(/[^a-z0-9]+/, '-').gsub(/(^-|-$)/, '')
end

def timestamp_title?(title)
  stripped = title.to_s.strip
  return false if stripped.empty?

  TIMESTAMP_PATTERNS.any? { |pattern| stripped.match?(pattern) }
end

def parse_next_link(header)
  return nil if header.nil? || header.empty?

  header.split(',').each do |link|
    return Regexp.last_match(1) if link =~ /<([^>]+)>;\s*rel="next"/
  end
  nil
end

def fetch_releases(repo, token: nil)
  releases = []
  url = URI("https://api.github.com/repos/#{repo}/releases?per_page=100")

  loop do
    request = Net::HTTP::Get.new(url)
    request['Accept'] = 'application/vnd.github+json'
    request['User-Agent'] = 'beautyjoy-release-news-script'
    request['Authorization'] = "Bearer #{token}" if token && !token.empty?

    response = Net::HTTP.start(url.host, url.port, use_ssl: true) do |http|
      http.request(request)
    end

    unless response.is_a?(Net::HTTPSuccess)
      raise "Failed to fetch #{url}: #{response.code} #{response.body}"
    end

    releases.concat(JSON.parse(response.body))

    next_link = parse_next_link(response['Link'])
    break unless next_link

    url = URI(next_link)
  end

  releases
end

def post_filename(date, repo_slug, release)
  identifier = release['tag_name'].to_s.empty? ? release['name'] : release['tag_name']
  "#{date}-#{repo_slug}-#{slugify(identifier)}.md"
end

# Render a template with %{name} placeholders. Unlike format/String#%, this
# does not interpret % characters inside the substituted values, so a release
# body containing "100%" or similar will not blow up.
def render_template(template, values)
  template.gsub(/%\{(\w+)\}/) { values.fetch(Regexp.last_match(1).to_sym).to_s }
end

def build_post(repo_config, release)
  date = Date.parse(release['published_at'] || release['created_at']).to_s
  display_title = release['name'].to_s.strip.empty? ? release['tag_name'] : release['name']
  full_title = "#{repo_config[:short_name]} Update: #{display_title}"
  url = release['html_url']
  intro = "A new release of #{repo_config[:short_name]} is available. " \
          'The release notes from GitHub are reproduced below.'

  contents = render_template(POST_BODY_TEMPLATE,
                             title: full_title.to_json,
                             date: date,
                             slug: repo_config[:slug],
                             url: url,
                             intro: intro,
                             body: release['body'].to_s.strip)

  filename = post_filename(date, repo_config[:slug], release)
  [filename, contents]
end

def parse_options(argv)
  options = { dry_run: false, verbose: false }
  OptionParser.new do |opts|
    opts.banner = 'Usage: generate_release_news.rb [options]'
    opts.on('--dry-run', 'Print what would be created without writing files') { options[:dry_run] = true }
    opts.on('-v', '--verbose', 'Verbose logging')                             { options[:verbose] = true }
    opts.on('-h', '--help', 'Show this help')                                 { puts opts; exit }
  end.parse!(argv)
  options
end

def main(argv)
  options = parse_options(argv)
  token = ENV['GITHUB_TOKEN']
  warn 'No GITHUB_TOKEN set; using unauthenticated API (60 req/hr).' if token.nil? || token.empty?

  FileUtils.mkdir_p(POSTS_DIR)

  stats = Hash.new(0)

  REPOS.each do |repo_config|
    warn "Fetching releases for #{repo_config[:repo]}..." if options[:verbose]
    releases = fetch_releases(repo_config[:repo], token: token)
    warn "  found #{releases.length} release(s)" if options[:verbose]

    releases.each do |release|
      tag = release['tag_name']

      if release['draft']
        stats[:skipped_draft] += 1
        next
      end

      title_for_check = release['name'].to_s.strip.empty? ? tag : release['name']
      if timestamp_title?(title_for_check)
        warn "  skip #{repo_config[:repo]} #{tag}: timestamp title" if options[:verbose]
        stats[:skipped_timestamp] += 1
        next
      end

      if release['body'].to_s.strip.empty?
        warn "  skip #{repo_config[:repo]} #{tag}: empty body" if options[:verbose]
        stats[:skipped_empty] += 1
        next
      end

      filename, contents = build_post(repo_config, release)
      path = File.join(POSTS_DIR, filename)

      if File.exist?(path)
        stats[:skipped_existing] += 1
        next
      end

      if options[:dry_run]
        warn "  would create #{filename}"
      else
        File.write(path, contents)
        warn "  created #{filename}" if options[:verbose]
      end
      stats[:created] += 1
    end
  end

  warn "Done. created=#{stats[:created]} existing=#{stats[:skipped_existing]} " \
       "draft=#{stats[:skipped_draft]} empty=#{stats[:skipped_empty]} " \
       "timestamp=#{stats[:skipped_timestamp]}"
end

main(ARGV) if __FILE__ == $PROGRAM_NAME
