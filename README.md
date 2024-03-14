# Server for browsing files on the cluster

Server inherits from Python's native HTTPS server to serve files in a grid.
To run, make sure you forward the port (default 8080) when you ssh into the server

```
ssh -L 8080:localhost:8080 siberian
```

or modify your `~/.ssh/config`

```
Host siberian
    HostName siberian.ist.berkeley.edu
    LocalForward 8080 localhost:8080
```

---

On the server, to install:

```
pip install git+ssh://git@github.com/vye16/cluster_fs.git
```

then, to run:

```
cluster_fs
```

or, for options:

```
cluster_fs --help
```
