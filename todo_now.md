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
- [x] Printer failsafe should display error in debug mode `(2019-12-28)`
- [x] Fix last ticket to pull getting stuck `(2019-12-26)`
- [x] Fix operators common task permissions: `(2019-12-26)`
> - [x] Operator shouldn't be able to `update`, `reset`, `delete` common tasks
> - [x] apply to all affected endpoints and templates
- [x] Refactor `reddit-wallpapers` and `json_stream` for cross-browse compatibility `(2019-12-25)`
- [x] Fix JS scripts IE11 compatibility `(2019-12-25)`
- [x] Remove Firefox notifier and ensure cross-browser compatibility `(2019-12-25)`
- [x] Remove new release notifier. Make it show up only on index page `(2019-12-25)`
- [x] fix browserNotifier when new release published __chrome bug__ `(2019-12-25)`
- [x] fix audio multimedia upload false detection `(2019-12-25)`
- [x] fix multimedia `webm` format upload, add `mp3` to supported files. `(2019-12-25)`
- [x] fix windows printing to rely fully on `wmic` command for shared printers detection. `(2019-12-28)`

- **Finally `IE 11` is fully supported 🚀**

- **Backend refactoring improved performance by 62% under heavy overload 🚀**
 
### To Add :

- [x] Display last pulled ticket in `tasks`, `offices` and `all_offices` `(2019-12-26)`
- [x] Decouple GUI and add command-line interface `(2019-12-22)`
- [x] ~~Add debug mode to GUI~~ `(2019-12-28)`

- [x] Database improvements and migration: `(2019-12-26)`
> - [x] ~~Add migrations scripts and setup~~
> - [x] Refactor structure for many-to-many relations in tasks to offices

- [ ] Export improvements and options:
> - [ ] Add json format to export `json`
> - [ ] Improve current `.csv` exporter


- [x] Initial integration test suite: `(2019-12-30)`
> - [x] Add testing db switch
> - [x] ~~Use `Flask-Testing`~~
> - [x] Cover and refactor all Administrate endpoints
