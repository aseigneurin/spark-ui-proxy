# Spark UI Proxy

If you are running a **Spark Standalone cluster behind a firewall** (let's say it is running on Amazon AWS), you might have issues accessing the UI of your cluster, especially because each worker has its own UI, making it difficult if not impossible to reroute all the ports using only SSH tunnels.

```
                          Firewall
                             |
                             |      ------------------------------
                             |      |        Spark Master        |
                             |      |  e.g. http://10.0.0.1:8080 |
                             |      ------------------------------
                             |
----------------------       |      ------------------------------
|    Your computer   | ----->X      |        Spark Worker        |
| e.g. 192.168.0.10  |       |      |  e.g. http://10.0.0.2:8080 |
----------------------       |      ------------------------------
                             |
                             |      ------------------------------
                             |      |        Spark Worker        |
                             |      |  e.g. http://10.0.0.3:8080 |
                             |      ------------------------------
                             |
```

This Python script creates a lightweight HTTP server that proxies all the requests to your Spark Master and Spark Workers. All you have to do is create a single SSH tunnel to this proxy, and the proxy will forward all the requests for you. All the links between the nodes will be functional.

```
                          Firewall
                             |
                             |                                     ------------------------------
                             |                                     |        Spark Master        |
                             |                                  -> |  e.g. http://10.0.0.1:8080 |
                             |                                 /    ------------------------------
                             |                                /
----------------------    tunnel    ------------------------ /     ------------------------------
|    Your computer   | -----------> |    spark-ui-proxy    | ----> |        Spark Worker        |
| e.g. 192.168.0.10  | :9999   :9999| http://10.0.0.1:9999 | \     |  e.g. http://10.0.0.2:8080 |
----------------------       |      ------------------------  \     ------------------------------
                             |                                 \
                             |                                  \  ------------------------------
                             |                                   ->|        Spark Worker        |
                             |                                     |  e.g. http://10.0.0.3:8080 |
                             |                                     ------------------------------
                             |
```

## How to use it

Start by creating an SSH tunnel from your computer to one of the nodes, let's say to the Spark Master:

```
$ ssh -L 9999:localhost:9999 <public IP/name of a node>
```

On this node, run the Python proxy:

```
$ python $BASEDIR/spark-ui-proxy.py localhost:8080 9999 &
```

You can stop the proxy at any time by hitting Ctrl+C.

Alternatively, you may run the proxy in background:

```
nohup python $BASEDIR/spark-ui-proxy.py localhost:8080 9999 &
```

Now, on your computer, open http://localhost:9999 and you should see the UI of your Spark cluster!
