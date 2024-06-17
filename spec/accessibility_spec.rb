# Run accessibility specs for all pages in the webiste.
# This runs the axe accessibility checker on each page in a headless browser.

# spec_helper ensures the webiste is built and can be served locally

require 'yaml'
require 'spec_helper'

# RSPEC_CONFIG_FILE = '_config.yml' or ENV['RSPEC_CONFIG_FILE']

def site_url
  @site_url ||= YAML.load_file(RSPEC_CONFIG_FILE)['url']
end

def load_site_urls
  puts "Running accessibility tests, expected deploy URL: #{site_url}"
  # TODO: Handle case where build is not in _site
  sitemap_text = File.read('_site/sitemap.xml')
  sitemap_links = sitemap_text.scan(/<loc>.+<\/loc>/)
  sitemap_links.filter_map do |link|
    link = link.gsub("<loc>#{site_url}", '').gsub('</loc>', '')

    next unless link.end_with?('.html') or link.end_with?('/')

    link
  end.sort
end

ALL_PAGES = load_site_urls
puts "Running tests on #{ALL_PAGES.count} pages."
puts "\t- #{ALL_PAGES.join("\n\t- ")}\n#{'=' * 50}\n\n"

ALL_PAGES.each do |path|
  describe "Page '#{path}' is accessible", type: :feature, js: true do
    before(:each) do
      visit(path)
    end

    it "according to WCAG 2.0 AA (REQUIRED)" do
      expect(page).to be_axe_clean.according_to(
        :wcag2aa, "path: #{path} does NOT meet WCAG 2.0 AA standards"
      )
    end
  end
end
