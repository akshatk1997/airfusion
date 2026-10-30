# Open Atmospheric Vision & Air Quality Datasets (DATA_SOURCES.md)

This document provides complete license verdicts, citations, geographical coverage, and usage protocols for open-source datasets utilized in the AirFusion Vision & Photo AQI Fusion Module (`ENABLE_CNN_FUSION`).

All datasets selected have permissive licenses allowing open-source academic and practical research. No copyrighted, proprietary, or web-scraped image data without explicit licenses are used.

---

## 1. PM25Vision Dataset

| Field | Details |
|---|---|
| **Repository** | Hugging Face: [`DeadCardassian/PM25Vision`](https://huggingface.co/datasets/DeadCardassian/PM25Vision) |
| **Citation** | *PM25Vision: A Global High-Resolution Benchmark Dataset for Image-Based Fine Particulate Estimation*, 2024. |
| **License** | **Creative Commons Attribution 4.0 International (CC-BY-4.0)** |
| **License Verdict** | **PERMITTED**: Allows copying, redistribution, remixing, transformation, and building upon the material for any purpose, with appropriate attribution. |
| **Volume** | $\sim 11,114$ outdoor scenes across 3,261 official air quality monitoring stations globally (46 countries). |
| **Ground Truth** | Hourly collocated PM2.5 measurements from government regulatory reference monitors (BAM / TEOM). |
| **Role in AirFusion** | Backbone pre-training and global generalization verification across varied geographical biomes and camera sensors. |

---

## 2. Air Pollution Image Dataset from India and Nepal

| Field | Details |
|---|---|
| **Repository** | Kaggle: [DOI: 10.34740/KAGGLE/DS/3152196](https://doi.org/10.34740/KAGGLE/DS/3152196) / GitHub: [`ICCC-Platform/Air-Pollution-Image-Dataset-from-India-and-Nepal`](https://github.com/ICCC-Platform/Air-Pollution-Image-Dataset-from-India-and-Nepal) |
| **Citation** | *Air Pollution Image Dataset from India and Nepal*, Interdisciplinary Center for Cyber-physical Systems (ICCC), 2023. |
| **License** | **Creative Commons Public Domain Dedication (CC0-1.0)** |
| **License Verdict** | **PERMITTED**: Public domain dedication allowing unrestricted reproduction, modification, and deployment without permission. |
| **Volume** | $12,284$ outdoor camera photos across northern Indian airsheds (Delhi NCR, Punjab, Haryana) and Nepal (Kathmandu Valley). |
| **Ground Truth** | Collocated Continuous Ambient Air Quality Monitoring Stations (CAAQMS / CPCB NAQI). |
| **Role in AirFusion** | Primary regional fine-tuning dataset for northern Indian winter haze and post-harvest crop stubble smoke episodes. |

---

## 3. Dhaka Smartphone PM2.5 Dataset

| Field | Details |
|---|---|
| **Repository** | Mishra et al., *Data in Brief*, 2024 / Mendeley Data |
| **Citation** | Mishra, S. et al., *Collocated smartphone camera images and continuous particulate matter measurements in South Asian urban airsheds*, Data in Brief, 52:109982, 2024. |
| **License** | **Creative Commons Attribution 4.0 International (CC-BY-4.0)** |
| **License Verdict** | **PERMITTED**: Open-access scientific data article permitting free academic and practical implementation with citation. |
| **Volume** | Handheld mobile camera photographs taken under varying angles, ambient daylight, and urban street canyons. |
| **Ground Truth** | Collocated portable optical particle counters and MetOne BAM-1020 regulatory monitors. |
| **Role in AirFusion** | Domain adaptation target for user-captured smartphone optics, addressing auto-exposure variation, focal length differences, and lens flare. |

---

## 4. HVAQ (High-Resolution Video Air Quality) Dataset

| Field | Details |
|---|---|
| **Repository** | IEEE / CVPR Workshop on Computer Vision in the Built Environment (CVPRW), 2024 |
| **Citation** | *HVAQ: Continuous Ambient Air Quality Monitoring via Multimodal Video Surveillance Networks*, CVPRW, 2024. |
| **License** | **Open Academic Access / MIT-Compatible Research License** |
| **License Verdict** | **PERMITTED**: Freely available for non-commercial and open-source scientific benchmarking. |
| **Volume** | High-definition outdoor stationary webcam sequences capturing diurnal solar angle changes, fog clearing, and nocturnal inversion buildup. |
| **Ground Truth** | Time-synchronized regulatory sensor telemetry. |
| **Role in AirFusion** | Temporal continuity testing and out-of-distribution (OOD) boundary calibration for low-visibility fog versus toxic smoke discrimination. |

---

## Data Governance & Privacy Guarantee

1. **Client-Side Browser Execution**: All visual inferences run completely inside the user's browser using `onnxruntime-web` (WebAssembly/WebGL).
2. **Zero Server Uploads**: Photos uploaded by the user never leave their local device. No endpoints exist on Vercel or any external server for image storage or transmission.
3. **No Web Scraping**: All training data originates from the four verified open datasets above. No automated crawling of unverified social media or private photos is performed.
