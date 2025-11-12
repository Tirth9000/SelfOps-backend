<p align="center">
  <img src="https://drive.google.com/uc?export=view&id=1j315k-0RZz6wOOmvSgu5M_k7T64rcYc5" alt="OwlOps Logo" width="400"/>
</p>

SelfOps is a unified CLI-based Docker monitoring tool that connects with your SelfOps web dashboard to provide real-time insights into containers running across multiple servers — from cloud to native.

## OwlOps Team

- [Tirth Sharma](https://github.com/Tirth9000)
- [Aditya Thakar](https://github.com/Araaditya)
- [Disha Sarvaiya](https://github.com/venellope04)
- [Sanskruti Gohil](https://github.com/Sanskruti-Gohil)

## Features

- 🚀 Monitor Docker containers across servers in real time
- ⚙️ CLI control — start, stop, restart, and inspect containers safely
- 🌐 Web dashboard integration for live stats and logs
- 🔄 Scalable architecture built using FastAPI, Socket.IO, and Redis
- 🧠 Future-ready — AI-powered insights and auto-recommendations (coming soon)

## Installation

Install library using python package manager.

```bash
pip install selfops
```

--> Signup into web/ create your account first to start with library commands. <--

```
selfops init --app_name-- --command--
```

**--commands--**

- -s or -select = to select which container to monitor by the application.
- -a or -all = automatically select all the container on the device.

Use this Commmand to start live data pipeline for web.

```
selfops live
```

**Extra commands**

You will get the information about this tool

```
selfops
```

Operational Commands

```
selfops monitor --container_name_or_id--
```

```
selfops start --container_name_or_id--
```

```
selfops stop --container_name_or_id--
```

```
selfops restart --container_nmae_or_id--
```

## Requirements

- Python 3.10 or higher
- Docker installed and running
- Internet access (for dashboard sync)

## License

[MIT](https://choosealicense.com/licenses/mit/)
