# FQM 0.4

## To Fix:

- [ ] CSS:
> - [ ] Move, improve general css to mstyle.css
> - [ ] Move all template inline css to style tag based on classes
> - [ ] Make google fonts default regardless of lang
> - [ ] use macros for inline css

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

- [x] Nested audio announcement: (5/7th)
~~ - use check boxes to get langs ~~
~~ - select field to enable disable announcement and toggle display check boxes ~~
> - [x] use nested tuples function generator instead (5/7th)

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
> - [ ] remove ar pics from watchIt


- [ ] More manage
> - [ ] add pull from all office
> - [ ] add general tasks (Require DB resign, Tasks over Offices)

- [x] implement uniqueness instead of dumb something() (5/4th)
> - [x] add option in uniqueness to always enforce hash tags (5/4th)
> - [x] get next, prev and customize btns working with hashtags (5/4th)
> - [x] uniqueness macro (5/4th)
> - [x] get sb_cust, sb_mange working with hashtags (5/5th)
> - [x] hashtag url based in the app .py files (5/5th)
> - [x] make disciple play well with the hashtags urls (5/5th)
> - [x] make sure forms error handling redirects to the hashtag url (5/4th)

- [ ] Create and use python module based on pos module for cross-platform drawn printing

- [ ] Smart tickets. Doubtful though !