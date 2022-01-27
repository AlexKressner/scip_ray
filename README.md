## Building a SCIP optimization factory with Ray on Azure
Most of us in ORMS know this situation: You have a neat MIP and want to run different experiments, i.e. use the same model with different problem data or solver settings. Consider the case where you do 75 experiments and each one takes 10 minutes. If you do the computations sequentially this sums up to 750 minutes or 12.5 hours. I remember the days when I started my laptop in the evening and had a look at the computations in the morning - to often just to notice that I have to change something (fix bugs, adjust the model, change the parameters, etc.) and do the computations again. 

What if you could easily spin up an arbitrary large cluster of high-performance virtual machines in the cloud and do massive optimization exeperiments in parallel? Something like a solver factory...! 

If this got you interest, have a look at this repo and see how to scale the non-commercial solver [SCIP](https://www.scipopt.org/index.php#about) with [Ray](https://www.ray.io) on Azure. For demonstration purposes, let's use the good old [capacitated lot sizing problem](https://www.sciencedirect.com/science/article/pii/S0305048303000598) and a small problem instance which SCIP can solve in approximately 27 seconds (optimization runs in one process with one CPU). Given a problem set of 100 of those small instances, **sequential execution** will be approx. **2700 seconds**. Spinning up a ray cluster with three virtual maschines (24 CPU) on Azure, **parallel execution** will give you a boost in experimentation speed of **factor 20** (**130 seconds** to solve all problem instances). 

## Files
- ``script.py``: SCIP implementation of CLSP and ray code
- ``config.yaml``: Config file to deploy ray cluster
- ``data/``: Folder containing problem data which is synced to nodes of ray cluster
- ``requirements.txt``: Python dependencies

## Getting started
**Note:** Ray is under heavy development and I have sometimes experienced issues in setting up a proper cluster. Most of the problems I had to deal with stem from the Azure SDK used in ray. In case of any problems have a look at the issues documented on github for ray. The ray command ``ray monitor config.yaml`` is helpful to see logs and to better understand bugs. I will have a look at new ray releases from time to time and pin dependencies when stable. At the moment I am pulling wheel files for ray from the latest master commit.


1. Make sure you have the [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli) installed 
2. Log in using ``az login``, then configure your credentials with ``az account set -s <subscription_id>``.
3. Clone repo
  ```sh
    git clone https://github.com/AlexKressner/scip_ray && cd scip_ray
  ```
4. Make a virtual environment and install dependencies. Ray is pinned to current master commit. Make sure to choose the [correct wheel](ttps://docs.ray.io/en/latest/installation.html) for your operating system - I am on MacOS!
  ```sh
    pip install -r requirements.txt
  ```
5. Configure the size of your cluster by editing ``config.yaml``(see syntax [here](https://docs.ray.io/en/latest/cluster/config.html))
    - Set the number of virtual machines: ``max_workers: 2``
    - Set the number of CPUs to use on each machine (head and worker nodes): ``resources: {"CPU": 8}``
    - Set the type of virtual machine to launch: ``Standard_F8s_v2`` (8 vCPUs and 16 GiB memory, more virtual machine types can be found [here](https://docs.microsoft.com/en-us/azure/virtual-machines/fsv2-series))
6. Make sure to increase your quotas on Azure to launch your cluster. See instructions [here](https://docs.microsoft.com/en-us/azure/azure-portal/supportability/per-vm-quota-requests).
7. Launch the cluster
  ```sh
    ray up -y config.yaml --no-config-cache
  ```
8. Run optimization in the cloud
  ```sh
    ray submit config.yaml script.py
  ``` 
9. Open another terminal and start ray dashboard
  ```sh
    ray dashboard config.yaml
  ```
10. Bring down the cluster
  ```sh
    ray down -y config.yaml
  ```



  