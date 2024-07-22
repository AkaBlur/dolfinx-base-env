# dolfinx Basic Setup for Docker

Base setup to use dolfinx inside docker (with JupyterLab)

## Prerequisites

- docker

## Usage

Usage is simple via `docker compose`:

**Start**
```bash
docker compose up -d
```

**Stop**
```bash
docker compose down
```

The container will open a JupyterLab environment on the machine that one can connect on:
[http://localhost:8888/](http://localhost:8888)

> [!WARNING]
> Please note that this image exposes a `root`-version of Jupyter!
> The JupyterLab server for this image is setup **without** any
> password protection or other methods of security!
>
> **Please set your networking / firewall setup accordingly to
> prevent any misuse!**

**Settings** of the JupyterLab instance are stored safely inside the local `settings` folder that gets mounted on start.
Therefore any changes in the JupyterLab environment will persist restarts.

An additional **kernel** to use inside the `dolfinx` docker environment is added to enable easier use of the real-mode `dolfinx` environment.

## Simulation Environment
This setup also includes some basic simulation functionality that I use. It is somewhat abstracted so that one can build a simple Jupyter notebook with some flexibility.

Simply create a `.ipynb` notebook inside `src` and import the necessary tools from `sim_tools`.

For simplicity one can **output** from this notebook to `../output` if files are generated. Therefore this directory can be used to **save results** on the local machine.

Currently implemented:
- Heat Transfer via Laplace Equation $\Delta u=0$
- 2D Rectangle Mesh
- Basic Boundary Conditions (Inward and Outward)
- Non-Linear Newton Solver
- Some Materials (glasses)

## Usage with other IDEs
To use this environment with another IDE (e.g. VSCode) instead of the default Jupyter web interface the following steps must be met:

1. Create the starting noteboook inside the web interface of Jupyter. Be sure to select the **correct kernel**!
2. It is recommended that you turn on the setting that the preferred kernel is **automatically started** (located inside *Notebook* under *Automatically Start Preferred Kernel*)
3. Inside your IDE, if it **supports Jupyter**, connect to the server on [http://localhost:8888/](http://localhost:8888/).
4. There should be an **existing** and **running kernel** listed. Choose this one as your default kernel inside the IDE.
5. Start your simulation 😄

If you are done, just close the IDE and shutdown the docker.

> [!NOTE]
> If you want to **continue** your work after you restarted the
> docker container simply open up the web interface and open the
> notebook your working on. <br><br>
> If you have not enabled the kernel auto-start you would then
> also have to start the kernel again.