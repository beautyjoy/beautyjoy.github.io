source "https://rubygems.org"

ruby '~> 2.7.5'

# Hello! This is where you manage which Jekyll version is used to run.
# When you want to use a different version, change it below, save the
# file and run `bundle install`. Run Jekyll with `bundle exec`, like so:
#
#     bundle exec jekyll serve
#
# This will help ensure the proper Jekyll version is running.
# Happy Jekylling!

gem "jekyll", "< 4"
gem "kramdown"
gem "kramdown-parser-gfm"
# Used for syncing content with aws
# aws.cs10.org is a backup site
gem 's3_website'

# This is the default theme for new Jekyll sites. You may change this to anything you like.
# gem "minima"

# If you want to use GitHub Pages, remove the "gem "jekyll"" above and
# uncomment the line below. To upgrade, run `bundle update github-pages`.
# gem "github-pages", group: :jekyll_plugins

# If you have any plugins, put them here!
group :jekyll_plugins do
  gem "jekyll-github-metadata", "~> 1.0"
  gem "jekyll-redirect-from"
  gem "jekyll-feed"
  gem "jekyll-sitemap"
  gem "jekyll-seo-tag"
end
