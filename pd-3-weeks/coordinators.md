--- title: Professional Development subtitle: Three-Week Workshop for Teachers layout: pd-3-weeks ---

### Site Coordinators

<div class="row grid-gallery">{% for profile in site.data.people.site-coordinators %}

<div class="col-sm-4 col-xs-6 grid-item">

<div class="circle-frame">{% include profile-photo.html image=profile.image name=profile.name %}</div>

<div class="caption">

#### {{ profile.name }}

{% if profile.location %}

###### {{ profile.location }}

{% endif %} {% if profile.description %}

{{ profile.description }}

{% endif %}</div>

</div>

{% endfor %}</div>
