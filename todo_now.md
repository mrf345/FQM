# FQM 0.7

### To Fix :

- [x] ~~Fix common task tickets bread crumbs counter~~ (2020-01-31)
> Default tickets incrementing behavior was altered which resolved the issue
- [ ] Refactor `manage` and `core` endpoints
- [x] Always hit tasks with office id to fix possible random redirection
- [ ] Arabic GUI fonts on Windows


### To Add :

- [ ] Pre-load waiting tickets from `/feed` to reduce text-to-speech generation latency.
- [ ] Add option to disable all the transition effects and reddit-wallpapers
- [ ] Pull random ticket from `tasks` or `offices`
- [ ] Option to display ticket number beside name on `display` screen
- [ ] Put random ticket on-hold

- [ ] Multiple Display screen support **based on offices**
> - [ ] Add multiple display screen routing
> - [ ] Add dynamic `/feed` to handle any office
> - [ ] Refactor display customization to handle multiple offices

- [ ] Add `core` and `manage` full test coverage
- [ ] Add windows build automation script
