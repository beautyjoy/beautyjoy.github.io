# The Beauty and Joy of Computing

[![CircleCI](https://circleci.com/gh/beautyjoy/beautyjoy.github.io.svg?style=svg)](https://circleci.com/gh/beautyjoy/beautyjoy.github.io)

This is the repo for the BJC homepage.

* [bjc.berkeley.edu – production](https://bjc.berkeley.edu)
* [beautyjoy.github.io – development](https://beautyjoy.github.io)

# Getting Started

bjc.berkeley.edu is built using [Jekyll][], a tool which builds static sities, mostly by compiling Markdown and some special formatting into HTML. Check out Jekyll's site for some good guides.

[Jekyll]: https://jekyllrb.com

The site is setup so you can probably get started by searching for page, and clicking the edit button right inside GitHub. (The edit button is located in the upper right controls for each file).

## Editing Content
Most pages can be updated simply by finding the file. Some pages are written in Markdown, which has a `.md` extension, but you can use HTML inside a markdown file.

If you're editing a file and see an `{% include ... %}` tag, you'll find that content inside the `_includes/` directory.

* All pages need to have "front matter", between the `---` to have them be processed. You can look at existing pages for an example.
* If you add the item `published: false`, the page will not be displayed. This is useful for when working on draft content.

## Editing Shared Components

### Includes

-  `section`: A horizontal section in a page's content.

    Usage: Capture the HTML for a section as the `section_content` variable before `include section.html`.

-  `profile-photo`: Generates the `img` tag for a person's profile photo, given the image link and name.
    Checks the provided image to see if it is a local file (in the `img/people` directory) or a remote URL, or use a blank avatar if no image is provided.

    Params: image (optional), name (optional)

-  `nav` is the main header for every page of the site.

## Configuration
- **Navigation**: The main site navigation is easily configurable.
	Take a look at [`_data/navbar.yml`](_data/navbar.yml), which is a list of links that will be rendered at the top of each page.
-   **Config**: By default, the `_config` file works for local development and GitHub pages. There are files for each server in `config/`.

-   **Adding a new post**: Simply create a new Markdown file in the `_posts` folder, as per default Jekyll behavior. It will also show up automatically on the "News" page.
	* _Make sure_, that each post contains the correct "front matter", between two `---`, otherwise it will not be rendered.
	* Posts that have a date in the future, will be displayed only once that date has arrived.
-   **Naming conventions**: As per HTML/CSS style guides, all HTML IDs and classes are separated by hyphens.
    Filenames *should* also be separated by hyphens (especially if they appear in user-facing URLs), but many of the image filenames are a mess.
    All Jekyll/template variables are using snake_case.

## Developing Locally (or in Cloud9)
You'll need Ruby installed on your computer, but that's it.

Assuming that's installed, this will get you fully setup.

```sh
git clone git@github.com:beautyjoy/beautyjoy.github.io.git
cd beautyjoy.github.io
gem install bundler
bundle install
bundle exec jekyll serve
```

After that you'll be able to access the site at [`http://localhost:4000`](http://localhost:4000). The next time you work on the site you'll only need to run `bundle exec jekyll serve`.

## Deployment
We're currently using GitHub pages as a review site. GitHub handles this automagically, and you can view the work on the master branch

The main site is bjc.berkeley.edu.

When new updates are ready, make a pull request from `master` to `berkeley` and everything will get updated in just a couple minutes.

[Make a pull request using this link.][pr-to-berkeley]

[pr-to-berkeley]: https://github.com/beautyjoy/beautyjoy.github.io/compare/berkeley...master?expand=1

Deployment is fairly straightforward, when the `berkeley` branch is updated, a process is kicked off that will build the site using the `_config_berkeley` file and then simply SCP the files to the proper folders.

The `bin/` directory and `circle.yml` include all the necessary steps for deployment.
