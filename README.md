# The Beauty and Joy of Computing

This is the repo for the BJC homepage.

* [View Live Version](http://bjc.berkeley.edu)
* [View Development Version](http://beautyjoy.github.io)

# Development

## Getting Started

This is built using Jekyll, a tool which helps build sites quickly.
-   **Config**: By default, the `_config` file works for local development and GitHub pages. There are files for each destination the site is hosted on.

-   **Adding a new post**: Simply create a new Markdown file in the `_posts` folder, as per default Jekyll behavior. It will also show up automatically on the News pages.

-   **Naming conventions**: As per HTML/CSS style guides, all HTML IDs and classes are separated by hyphens.
    Filenames *should* also be separated by hyphens (especially if they appear in user-facing URLs), but many of the image filenames are a mess.
    All variables are underscore-separated, as you would expect.

## Pages

Header options:
- `title`
- `subtitle`
- `header_background`: If an image background is desired, choose one of the JPEGs in the `/img/backgrounds` folder, e.g. `class1`, `class2`, `class3` or `class4`

## Layouts

You should only ever need to use the `page` layout. It provides the standard page with navbar, title header jumbotron and footer.

For pages containing content split into separate subpages, an additional layout is used to provide the reusable nav menu between subpages. These layouts are:
- `pd-3-weeks`
- `pd-6-weeks`
- `team`

## Includes

-   `section`: A horizontal section in a page's content.

    Usage: Capture the HTML for a section as the `section_content` variable before `include section.html`.

-   `profile-photo`: Generates the `img` tag for a person's profile photo, given the image link and name.
    Checks the provided image to see if it is a local file (in the `/img/people` directory) or a remote URL, or use a blank avatar if no image is provided.

    Params: image (optional), name (optional)

## Deployment
here.
We're currently using GitHub pages as a review site. GitHub handles this automagically, and you can view the work on the master branch t

The main site is bjc.berkeley.edu.

Deployment is fairly straightforward, when the `berkeley` branch is updated, a process is kicked off that will build the site using the `_config_berkeley` file and then simply SCP the files to the proper folders.

When new updates are ready, make a pull request from `master` to `berkeley` and everything will get updated in just a couple minutes.

The `bin/` directory and `circle.yml` include all the necessary steps for deployment.
