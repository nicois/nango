# aims

## async all the way down (to the views at least), including middleware

- ensure sync middleware etc is being logged if there is a switch, to make sure we are staying async

## use arq for async job management (if required/applicable)

## CAS-like locking patterns (for optimistic-style updates, without an exclusive lock)

- when a form is being generated, add additional hidden fields with the original value. If, when the form is submitted, this value does not match the current value in the DB, then reject the change
- need to think about whether there are complications with multi-model forms etc

## allow fields (form fields, or more general?) to receive live updates via a common websocket, if their values change on the server

- add a command to a base template which will include the common JS code.
- use a macro command in a template to register a DOM object against a variable name.
- when the register macro is called for the first time, lazily create the websocket connection. then push the variables up the websocket to register them, listening for updates
- how do we manage auth? rely on django model permissions.. registration ws will use the fully-qualified model name and pkey

## allow locking of models (to prevent concurrent modification)

- use redis with NX to take out a lock.
- probably reuse the WS connection below to keep it alive. possibly require the field / DOM element to be registered before locking is awailable

## rich widgets

- take "simple" model validation rules and automatically apply then client-side (take this from early horizon commit?)
- allow widgets to have associated JS code which runs when the value is modified (or on blur?)
- leverage the WS to pipe values back to the server and perform server-side provisional validation (rolling back the transaction afterwards), notifying in realtime (with debounce/cooldown)
