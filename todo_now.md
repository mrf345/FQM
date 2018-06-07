# FQM 0.4

## To Fix:

- [x] CSS: (6/1st)
> - [x] use less flask-less (6/1st)
> - [x] replace brp with pt (6/1st)
> - [x] Move, improve general css to mstyle.css (6/1st)
> - [x] Move all template inline css to style tag based on classes (6/1st)
> - [x] Make google fonts default regardless of lang (6/1st)
> - [x] use macros for inline css (6/1st)

- [x] JsonStream:
> - [x] Fix mdruation and effect_duration

- [x] Fix date in printed ticket (6/8th)
> from UTC now to local datetime

- [x] Template: (6/1st)
> - [x] look for template repetitiveness and replace it with macros (6/1st)
> - [x] replace manage panel headers and footers with macros (6/1st)
> - [x] replace background css in base and base_s with macro (6/1st)

- [x] Nested audio announcement: (5/7th)
> ~~use check boxes to get langs~~
> ~~select field to enable disable announcement and toggle display check boxes~~
> - [x] use nested tuples function generator instead (5/7th)

- [x] initial disciple with uniqueness: (5/11th)
> - [x] figure out way to get the initial url hashed in display_c, touch_c and, slide_a (5/11th)

- [x] Delete all offices (5/11th)
> - [x] fix delete all false reset request (5/11th)

- [x] Un-bundled JS (5/12th)
> - [x] make sure of unique toReturn values in all un-bundled js scripts. to avoid future clashes. (5/12th)

- [ ] Fix type of ticket displayed
> - [ ] All offices
> - [ ] Tasks
> - [ ] Offices

- [ ] GUI smaller sized font for server status


## To Add:

- [x] GUI Multilang: (5/10th)
> - [x] add fr, es, it to static langs (5/10th)
> - [x] replace langs buttons with select field (5/10th)

- [x] Adding new release notifier (5/19th)
> - [x] modify browser_notifier (5/19th)
> - [x] implement new browser_notifier (5/19th)

- [ ] Adding alias
> - [ ] add alias to display_screen customize settings
> - [ ] add alias to printed ticket settings
> - [ ] alias for task and office in display and display/announcement
> - [ ] alias for task and office in app/languages

- [x] Recall announcement (6/8th)
> - [x] add special recall value /feed (6/8th)
> - [x] add exception to repeat on display.html when special /feed value met (6/8th)

- [x] Implement flask_googletrans: (6/5th)
> - [x] add fr, es, it en to /lang (6/5th)
> - [x] fix extra_function get_lang, __Add warning if cache not found and fail to connect__ (6/5th)
> - [x] add langs to dropdown menu base.html (6/5th)
> - [x] put back and cache all flash messages (6/5th)
> - [x] cache wtforms and remove ar_forms (6/5th)
> - [x] remove ar from templates and cache templates (6/5th)
> - [x] remove ar from app/* and cache them (6/5th)
> - [x] remove ar pics from watchIt (6/5th)


- [x] implement uniqueness instead of dumb something() (5/4th)
> - [x] add option in uniqueness to always enforce hash tags (5/4th)
> - [x] get next, prev and customize btns working with hashtags (5/4th)
> - [x] uniqueness macro (5/4th)
> - [x] get sb_cust, sb_mange working with hashtags (5/5th)
> - [x] hashtag url based in the app .py files (5/5th)
> - [x] make disciple play well with the hashtags urls (5/5th)
> - [x] make sure forms error handling redirects to the hashtag url (5/4th)
> - [x] add special hash callback for disciple to solve remind me later (5/12th)

- [x] browser detection: (5/12th)
> - [x] move specific browser css to macros (5/12th)
> - [x] create and utilize browser_notifier front-end solution (5/12th)
> - [x] remove browser detection from back-end (5/12th)

- [x] Implement flask_gtts **Fixing ticket repeating announcement** (6/3rd)
> - [x] use gTTS from the display template instead (6/3rd)
> - [x] remove values from db (6/3rd)
> - [x] remove old values from display template (6/3rd)
> - [x] test if that solves repeating same name (6/3rd)
