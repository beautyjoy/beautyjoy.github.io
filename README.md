# Official Site for the Beauty and Joy of Computing

This is a static site written using the Jekyll framework.

## Getting Started

-   Config: **Remember to update the `baseurl` and `url` in `_config.yml` to wherever the site is hosted.**
    The config you are seeing now is probably set to work with a version hosted on Github Pages.

    Remember to run Jekyll with the `--baseurl` option:
    `jekyll s --baseurl <baseurl>`

-   Adding a new post: Simply create a new Markdown file in the `_posts` folder, as per default Jekyll behavior. It will also show up automatically on the News pages.

-   Naming conventions: As per HTML/CSS style guides, all HTML IDs and classes are separated by hyphens. All filenames are also separated by hyphens, since they might appear in URLs.
    All variables are underscore-separated, as usual.

## Pages

Header options:
- `title`
- `subtitle`
- `header_background`: If an image background is desired, choose one of the JPEGs in the `/img/backgrounds` folder, e.g. `class1` `class2` `class3` `class4`

## Layouts

You should only ever need to use the `page` layout. It provides the standard page with navbar, title header jumbotron and footer.

For pages containing content split into separate subpages, an additional layout is used to provide the reusable nav menu between subpages. These layouts are:
- `pd-3-weeks`
- `pd-6-weeks`
- `team`

## Includes

-   `section`: A horizontal section in a page's content.

    Usage: Capture the HTML for a section as the `section_content` variable before `include section.html`.

-   `profile_photo`: Generates the `img` tag for a person's profile photo, given the image link and name.
    Checks the provided image to see if it is a local file (in the `/img/people` directory) or a remote URL, or use a blank avatar if no image is provided.

    Params: image (optional), name (optional)

## Data Files

-   Profile photos: `image` can be the filename (including extension) of a local file in the `/img/people` folder, the URL of a remote image, or blank

-   Why are some data files in CSV format, while others in YAML?

    YAML allows for more free-form data as opposed to the more structured CSV.
    Also, the data files in the `people` folder are in CSV because the team data was initially envisioned as only one page,
    with straightforward data columns for each person. As the team data grew in complexity and volume, the quickest (and laziest)
    way was simply to have multiple CSV files.


