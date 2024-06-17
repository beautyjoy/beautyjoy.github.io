# Run accessibility specs for all pages in the webiste.
# This runs the axe accessibility checker on each page in a headless browser.
# This assumes that the website is running locally on port 4000.

# TODO: See if we can share this with spec_helper.rb
require 'yaml'
require 'spec_helper'

# RSPEC_CONFIG_FILE = '_config.yml' or ENV['RSPEC_CONFIG_FILE']

def site_url
  YAML.load_file(RSPEC_CONFIG_FILE)['url']
end

def load_site_urls
  deploy_url = site_url
  # TODO: Handle case where build is not in _site
  sitemap_text = File.read('_site/sitemap.xml')
  sitemap_links = sitemap_text.scan(/<loc>.+<\/loc>/)
  sitemap_links.filter_map do |link|
    link = link.gsub("<loc>#{deploy_url}", '')
    link = link.gsub('</loc>', '')

    next unless link.end_with?('.html') or link.end_with?('/')

    link
  end
end

$ALL_PAGES = load_site_urls

$ALL_PAGES.each do |page|
  describe "Page #{page} is accessible", type: :feature, js: true do
    before(:each) do
      visit(page)
    end

    it "according to WCAG 2.0 AA (REQUIRED)" do
      expect(page).to be_axe_clean.according_to(
        :wcag2aa, "path: #{page} does NOT meet WCAG 2.0 AA standards"
      )
    end
  end
end
