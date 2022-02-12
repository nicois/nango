The following command will create and start a webserver for a
demonstration project, allowing you to easily experience the capabilities
of the nango Django extension.

```bash
./quickstart.sh
```

Specifically, the script will

- create a python virtualenv in your temporary directory
- install Django and a few other packages
- start a Django development server listening on port 8000 locally

To interact with the demo, while the Django server is running, you can:

- navigate to the admin panel for customers (http://localhost:8000/admin/demo/customer/). Administrator username and password are both 'admin'.
- navigate to a very basic UpdateView for one of the existing customers http://localhost:8000/demo/1/)
