# FQM 0.5

## To Fix :

- [ ] better cross platform JS
> - [ ] rewrite unbundled audio_sequence with date() for random
> - [ ] rewrite unbundled redditWallpapers
> - [ ] remove error handling from all
> - [ ] create flask_slimit and use with cache

- [ ] flask_less multi files hashing and caching

- [ ] rewrite and comment back-end code for better performance and support

- [x] repeat announcements 23/July
> - [x] replace session storage with db storage on /feed 23/July
> - [x] move it from partial front-end to full back-end 23/July

- [ ] Default button to aliases to restore default options
- [ ] Add flash message to language change

## To Add :

- [ ] Create and use python module based on pos module for cross-platform drawn printing

- [ ] Improve User management:
> - [ ] add configurable profile for users
> - [ ] add activities log to profile
> - [ ] improve office operators interface

- [ ] create smart tickets display
> - [ ] method to generate special identifier for the device based on time + date + randint
> - [ ] new serial for s-tickets that generates ticket with the special identifier stored in db
> - [ ] new feed for s-tickets that takes special identifer as an arg
> - [ ] s-ticket layout integrated with json_stream and audio_sequence 

- [ ] New Tickets
> - [ ] add printed tickets section from old tickets
> - [ ] add registered tickets section with new settings like name, number, message color text font and button color text font
> - [ ] add s-ticket layout customization background title colors fonts sound notification and audio notification
> - [ ] add special args for touch_screen to redirect to registered or printed tickets
> - [ ] remove old tickets from template and db

- [ ] Printed ticket customization
> - [ ] to choose width and height of text
> ***To fix scaling issue***
> - [ ] to chose which information to be displayed

- [ ] More manage
> - [ ] add pull from all office
> - [ ] add general tasks (Require DB resign, Tasks over Offices)

- [ ] Documentation:
> - [ ] Github wiki docs instead of pdf
> - [ ] Video tutorials: demo, setup, configuration cross-platform