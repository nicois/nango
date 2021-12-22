formsets
admin panel - fieldsets?
security - allow (non-anonymous) user to retrieve model info for these instances for a minute
delay ws by X seconds

idea: subclass the form and in **init** patch the fields to render with the extra hidden bit automatically. this would mean we don't need to override all the places the field could be rendered
