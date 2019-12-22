# FQM 0.6

### To Fix :

- [x] Migrate code from Python 2 and PySide to Python 3 and PyQT5 `(2019-12-22)`
- [x] Customization multimedia page bug `(2019-12-22)`
- [x] Use latest `flask_minify` to fix high memory consumption `(2019-12-22)`
- [x] Use latest `audio_sequence` to fix overwriting files `(2019-12-22)`
- [ ] Use one source of truth for all translations GUI and app `gt_cached.json`
- [ ] Use mixIns to modularize and cleanup backend
- [ ] Printer failsafe should display error in debug mode
- [ ] Fix last ticket to pull getting stuck
- [ ] Refactor `reddit-wallpapers` for cross-browse compatibility
- [ ] Fix JS scripts IE11 compatibility
- [ ] Remove Firefox notifier and ensure cross-browser compatibility
- [ ] Remove new release notifier. Make it show up only on index page
- [ ] fix browserNotifier when new release published __chrome bug__

### To Add :

- [x] Decouple GUI and add command-line interface `(2019-12-22)`
- [ ] Add debug mode to GUI

- [ ] Database improvements and migration:
> - [ ] Add migrations scripts and setup
> - [ ] Refactor structure for many-to-many relations in tasks to offices

- [ ] Export improvements and options:
> - [ ] Add json format to export `json`
> - [ ] Improve current `.csv` exporter

- [ ] System on-hold:
> - [ ] Put whole system on-hold, with customized message output.
> - [ ] Put a screen on-hold, with customized message output.
> - [ ] Auto hold system, whenever numbers of tickets past certain number.

- [ ] Initial integration test suite:
> - [ ] Add testing db switch
> - [ ] Use `Flask-Testing`
> - [ ] Cover all Administrate endpoints
