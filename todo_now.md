# FQM 0.6

### To Fix :

- [x] Migrate code from Python 2 and PySide to Python 3 and PyQT5 `(2019-12-22)`
- [x] Customization multimedia page bug `(2019-12-22)`
- [x] Use latest `flask_minify` to fix high memory consumption `(2019-12-22)`
- [x] Use latest `audio_sequence` to fix overwriting files. And replace `fetch` with `ajax` for IE `(2019-12-25)`
- [x] Use one source of truth for all translations GUI and app `gt_cached.json` `(2019-12-23)`
- [x] Use mixIns to modularize and cleanup backend `(2019-12-24)`
- [x] Fix `/feed` and announcements after migration to py3 `(2019-12-24)`
- [x] Fix reset office from within itself `(2019-12-24)`
- [x] Fix search SQLAlchemy safe parameters, after migration to Python 3 bug `(2019-12-24)`
- [ ] Printer failsafe should display error in debug mode
- [ ] Fix last ticket to pull getting stuck
- [x] Refactor `reddit-wallpapers` and `json_stream` for cross-browse compatibility `(2019-12-25)`
- [x] Fix JS scripts IE11 compatibility `(2019-12-25)`
- [x] Remove Firefox notifier and ensure cross-browser compatibility `(2019-12-25)`
- [x] Remove new release notifier. Make it show up only on index page `(2019-12-25)`
- [x] fix browserNotifier when new release published __chrome bug__ `(2019-12-25)`

**Finally `IE 11` is fully supported 🚀**

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
> - [ ] Cover and refactor all Administrate endpoints
