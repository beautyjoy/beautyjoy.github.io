# The Beauty and Joy of Computing

This is the repo for the BJC homepage.

* [View Live Version](http://bjc.berkeley.edu)
* [View Development Version](http://beautyjoy.github.io)

# Development

## Getting Started

-   **Config**: *Remember to update the `baseurl` and `url` in `_config.yml` to wherever the site is hosted!*
    The config you are seeing now is probably set to work with a version hosted on Github Pages.

    Remember to run Jekyll with the `--baseurl` option:
    `jekyll s --baseurl <baseurl>`

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


