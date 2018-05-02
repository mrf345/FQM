# FQM 0.4

## To Fix:

- [ ] CSS:
> - [ ] Move, improve general css to mstyle.css
> - [ ] Move all template inline css to style tag based on classes

- [ ] JsonStream:
> - [ ] Fix mdruation and effect_duration 

- [ ] Template:
> - [ ] look for template repetitiveness and replace it with macros
> - [ ] replace manage panel headers and footers with macros
> - [ ] replace background css in base and base_s with macro

- [ ] Improve User management:
> - [ ] add configurable profile for users
> - [ ] add activities log to profile
> - [ ] improve office operators interface

- [ ] Nested audio announcement:
> - [ ] use check boxes to get langs
> - [ ] select field to enable disable announcement and toggle display check boxes

## To Add:

- [ ] GUI Multilang:
> - [ ] add fr, es, it to static langs
> - [ ] replace langs buttons with select field

- [ ] Implement flask_googletrans:
> - [ ] add fr, es, it en to /lang
> - [ ] fix extra_function get_lang, __Add warning if cache not found and fail to connect__
> - [ ] add langs to dropdown menu base.html
> - [ ] put back and cache all flash messages
> - [ ] cache wtforms and remove ar_forms
> - [ ] remove ar from templates and cache templates
> - [ ] remove ar from app/* and cache them


- [ ] More manage
> - [ ] add pull from all office
> - [ ] add general tasks (Require DB resign, Tasks over Offices)

- [ ] implement uniqueness instead of dumb something()
> - [ ] add option in uniqueness to always enforce hash tags
> - [ ] get next, prev and customize btns working with hashtags
> - [ ] get sb_cust, sb_mange working with hashtags
> - [ ] hashtag url based in the app .py files
> - [ ] make disciple play well with the hashtags urls
> - [ ] make sure forms error handling redirects to the hashtag url

- [ ] Create and use python module based on pos module for cross-platform drawn printing

- [ ] Smart tickets. Doubtful though !