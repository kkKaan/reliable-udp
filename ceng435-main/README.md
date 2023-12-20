
Install docker and VSCode on your sytstem

Go to your favorite development folder on your local machine and run

```
   git clone https://github.com/cengwins/ceng435.git
```

Open this folder (ceng435) in VSCode

Open a terminal in VSCode, under the ceng435 directory where the Dockerfile resides run

```
   docker build -t ceng435 .
```

After the image is built

You can run the following to get the server machine
```
   docker run -t -i --rm --privileged --cap-add=NET_ADMIN --name ceng435server -v ./code:/app:rw ceng435:latest bash
```

and the following for the client machine

```
   docker run -t -i --rm --privileged --cap-add=NET_ADMIN --name ceng435client -v ./code:/app:rw ceng435:latest bash
```

and you will be in your virtual Ubuntu 22.04 machines (python installed). Note that if you develop code in these virtual machines, if you stop the machine your code will be lost. That is why I recommend you to use Github to store your code and clone in the machine, and push your code to Github before shutting the virtual machine down. The other option is to work in the /app folder in your virtual machine which is mounted to the "code" directory of your own machine.

**IMPORTANT** Note that the "code" folder on your local machine is mounted to the "/app" folder in the virtual machine (read/write mode). You can use these folders (they are the same in fact) to develop your code. Other than the /app folder, this tool does not guarantee any persistent storage: if you exit the virtual machine, all data will be lost.

After running the Ubuntu Docker, you can type "ip addr" to see your network configuration. Work on eth0.

Docker extension of vscode will be of great benefit to you.

In the server terminal, move to the **"objects" folder** and run

```
   ./generateobjects
```

to generate 10 small (10K) and 10 large (10M) objects together with their md5 checksums.

Some tc commands that may be of help to you can be found at https://man7.org/linux/man-pages/man8/tc-netem.8.html and https://www.cs.unm.edu/~crandall/netsfall13/TCtutorial.pdf

You will analyze the impact of delay, packet loss percentage, corrupt packet percentage, duplicate percentage, reorder percentage on the total time to download all 20 objects. You will plot figures for each parameter (delay, loss, ...) where the x-axis of the figure will have various values for these parameters and the y-axis will be the total time to download 20 objects. There will be two curves in each figure, one for TCP and the other curve for your UDP-based RDT implementation together with interleaving technique.



