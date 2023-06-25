# DAS Blender Render

A distributed Blender render framework

[![city.gif](https://i.postimg.cc/VNcs7XDF/city.gif)](https://postimg.cc/hXpqvQFJ)
Example render based on the [Scans Island](https://krynski.artstation.com/projects/DAKRZE) project by Art Director &
Concept Artist [Piotr Krynski](https://krynski.artstation.com/). Modified to have a camera flying around the
environment.

## Description

DAS Blender Render is built in native Python 3.6. It uses Blender 3.3 LTS as the designated Blender version. 
Designed for usage on DAS-6.

## Deploy

Deploying the system requires the following steps:

1. Clone the project to the `/home/$USER` directory.
2. Change the chmod permissions of deploy.sh
3. Execute deploy.sh, first value is the master node, following values are workers. For
   example `deploy.sh node301,node302,node303`
4. Initiate a Blender client by setting up a `config.yaml` file (use `example-config.yaml` as reference).
   See `async-blender-call.py` for example.
5. Execute the blender client.

## Development

1. Clone the project
2. Copy the `example-config.yaml` and rename it to `config.yaml`.
3. Start the `test/master-test.py`
4. Start the `test/worker-test.py`
5. A cluster has now been started. You can create a new client to execute a blender render, See `async-blender-call.py`
   for example.

The demo project of the GIF can be found on: [brandonkroes.com](https://brandonkroes.com/DDPS/1080p60fps.blend)


