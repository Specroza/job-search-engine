"""
Job Listings Search Engine — Streamlit Web UI
Google-style interface for the Data Mining Lab Project
Run with: streamlit run app.py
"""

import re
import math
import streamlit as st

# ── Try NLTK; fall back to a manual stopword list if not installed ──────────
try:
    import nltk
    nltk.download("stopwords", quiet=True)
    nltk.download("punkt", quiet=True)
    from nltk.corpus import stopwords
    from nltk.stem import PorterStemmer
    STOPWORDS = set(stopwords.words("english"))
    stemmer = PorterStemmer()
    def stem(w):
        return stemmer.stem(w)
except Exception:
    STOPWORDS = {
        "a","an","the","and","or","but","in","on","of","to","for",
        "is","are","was","were","be","been","with","at","by","from",
        "as","it","its","we","you","your","our","their","this","that",
        "will","can","not","have","has","had","do","does","did","they",
        "he","she","i","me","my","we","us","who","which","what","how",
        "if","up","out","about","into","than","so","all","also","more",
        "need","needed","needing","required","require","experience",
        "strong","knowledge","skills","skill","using","use","used",
        "able","ability","work","working","build","building","design",
        "designing","must","may","including","include","included",
    }
    def stem(w):
        # Lightweight Porter-like suffix stripping
        for suffix in ("ing", "tion", "ment", "ness", "ity", "er", "ed", "s"):
            if w.endswith(suffix) and len(w) - len(suffix) > 2:
                return w[: -len(suffix)]
        return w


# ════════════════════════════════════════════════════════════
#  DATASET — 100 Job Listings
# ════════════════════════════════════════════════════════════
JOB_LISTINGS = [
    {"id": 1, "title": "Python Backend Developer", "company": "TechCorp BD", "location": "Dhaka",
     "description": "We are looking for an experienced Python developer to build and maintain backend APIs using Django and FastAPI. Proficiency in SQL and PostgreSQL required. Experience with Docker and REST APIs is a plus.",
     "tags": ["python", "django", "fastapi", "backend", "sql", "postgresql"]},
    {"id": 2, "title": "Data Scientist", "company": "Analytics Hub", "location": "Dhaka",
     "description": "Seeking a data scientist skilled in machine learning, Python, and data analysis. You will build predictive models using scikit-learn and TensorFlow. Knowledge of statistics and data visualization required.",
     "tags": ["data science", "machine learning", "python", "tensorflow", "statistics"]},
    {"id": 3, "title": "Frontend React Developer", "company": "WebWave", "location": "Chittagong",
     "description": "Join our team as a frontend developer with strong skills in React, JavaScript, and CSS. Experience with Redux, REST APIs, and responsive design is essential. TypeScript knowledge is a bonus.",
     "tags": ["react", "javascript", "css", "frontend", "redux", "typescript"]},
    {"id": 4, "title": "Machine Learning Engineer", "company": "AI Ventures", "location": "Dhaka",
     "description": "We need a machine learning engineer to develop and deploy ML models at scale. Proficiency in Python, PyTorch, and TensorFlow required. Knowledge of MLOps and cloud platforms like AWS is preferred.",
     "tags": ["machine learning", "python", "pytorch", "tensorflow", "mlops", "aws"]},
    {"id": 5, "title": "DevOps Engineer", "company": "CloudBase", "location": "Remote",
     "description": "Looking for a DevOps engineer with expertise in AWS, Docker, Kubernetes, and CI/CD pipelines. Experience with Terraform and Linux system administration required.",
     "tags": ["devops", "aws", "docker", "kubernetes", "ci/cd", "terraform", "linux"]},
    {"id": 6, "title": "Full Stack Developer", "company": "StartupX", "location": "Dhaka",
     "description": "Full stack developer needed for a fast-growing startup. Skills required: Node.js, React, MongoDB, and REST API design. Experience with agile development and Git version control preferred.",
     "tags": ["nodejs", "react", "mongodb", "fullstack", "rest", "git"]},
    {"id": 7, "title": "Software QA Engineer", "company": "QualityFirst", "location": "Sylhet",
     "description": "QA engineer required with experience in manual and automated testing. Proficiency in Selenium, pytest, and JIRA needed. Understanding of software development lifecycle and bug tracking required.",
     "tags": ["qa", "testing", "selenium", "pytest", "automation", "jira"]},
    {"id": 8, "title": "Database Administrator", "company": "DataSafe Ltd", "location": "Dhaka",
     "description": "Experienced DBA needed to manage MySQL, PostgreSQL, and MongoDB databases. Responsibilities include performance tuning, backup management, and database security. SQL optimization skills essential.",
     "tags": ["dba", "mysql", "postgresql", "mongodb", "sql", "database"]},
    {"id": 9, "title": "Android Mobile Developer", "company": "AppFactory", "location": "Dhaka",
     "description": "Android developer required with strong Kotlin and Java skills. Experience building apps with Jetpack Compose, Retrofit, and Firebase. Understanding of Material Design and Google Play Store deployment.",
     "tags": ["android", "kotlin", "java", "mobile", "firebase", "jetpack"]},
    {"id": 10, "title": "iOS Developer", "company": "MobileMinds", "location": "Remote",
     "description": "Experienced iOS developer needed with Swift and Objective-C expertise. Must have knowledge of UIKit, SwiftUI, Core Data, and App Store submission process. REST API integration experience required.",
     "tags": ["ios", "swift", "objective-c", "swiftui", "xcode", "mobile"]},
    {"id": 11, "title": "Cybersecurity Analyst", "company": "SecureNet", "location": "Dhaka",
     "description": "Cybersecurity analyst required to monitor and protect network infrastructure. Skills needed: penetration testing, vulnerability assessment, firewall management, and knowledge of OWASP guidelines.",
     "tags": ["cybersecurity", "penetration testing", "network", "firewall", "owasp"]},
    {"id": 12, "title": "UI/UX Designer", "company": "DesignStudio", "location": "Dhaka",
     "description": "Creative UI/UX designer with expertise in Figma, Adobe XD, and user research. Strong portfolio required demonstrating web and mobile design. Knowledge of design systems and accessibility standards.",
     "tags": ["ui", "ux", "design", "figma", "adobe xd", "user research"]},
    {"id": 13, "title": "Data Analyst", "company": "InsightCo", "location": "Chittagong",
     "description": "Data analyst needed with skills in Excel, SQL, Python, and Power BI. Responsibilities include data cleaning, dashboard creation, and reporting. Strong analytical and communication skills required.",
     "tags": ["data analysis", "sql", "python", "power bi", "excel", "reporting"]},
    {"id": 14, "title": "Cloud Architect", "company": "SkyTech", "location": "Remote",
     "description": "Senior cloud architect needed to design and implement AWS and Azure solutions. Experience with cloud migration, microservices, serverless architecture, and cost optimization required.",
     "tags": ["cloud", "aws", "azure", "architect", "microservices", "serverless"]},
    {"id": 15, "title": "NLP Research Engineer", "company": "LangAI", "location": "Dhaka",
     "description": "NLP engineer needed to work on natural language processing models. Experience with transformers, BERT, GPT models, and HuggingFace required. Python and PyTorch skills essential.",
     "tags": ["nlp", "natural language processing", "python", "bert", "transformers", "pytorch"]},
    {"id": 16, "title": "Blockchain Developer", "company": "ChainTech", "location": "Remote",
     "description": "Blockchain developer needed with experience in Solidity, Ethereum, and smart contracts. Knowledge of Web3.js, DeFi protocols, and NFT development. Python or JavaScript background preferred.",
     "tags": ["blockchain", "solidity", "ethereum", "smart contracts", "web3", "nft"]},
    {"id": 17, "title": "Network Engineer", "company": "NetSolutions", "location": "Dhaka",
     "description": "Network engineer required to design and manage enterprise networks. Expertise in Cisco routers, switches, VPN configuration, and network monitoring tools. CCNA or CCNP certification preferred.",
     "tags": ["networking", "cisco", "vpn", "ccna", "linux", "infrastructure"]},
    {"id": 18, "title": "Product Manager", "company": "ProductHouse", "location": "Dhaka",
     "description": "Experienced product manager needed to lead software product development. Skills required: roadmap planning, stakeholder management, agile, user story writing, and data-driven decision making.",
     "tags": ["product management", "agile", "scrum", "roadmap", "stakeholder"]},
    {"id": 19, "title": "Java Spring Boot Developer", "company": "EnterpriseApps", "location": "Dhaka",
     "description": "Java developer required with Spring Boot, Hibernate, and Microservices experience. Knowledge of REST APIs, Maven, Jenkins CI/CD, and MySQL database required. Experience with Docker is a plus.",
     "tags": ["java", "spring boot", "hibernate", "microservices", "mysql", "docker"]},
    {"id": 20, "title": "Game Developer", "company": "GameZone", "location": "Dhaka",
     "description": "Game developer needed with Unity and C# skills. Experience in 2D and 3D game development, physics simulation, and game optimization. Knowledge of Blender for 3D modeling is a bonus.",
     "tags": ["game development", "unity", "c#", "3d", "blender", "simulation"]},
    {"id": 21, "title": "Business Intelligence Developer", "company": "BIWorks", "location": "Dhaka",
     "description": "BI developer needed with Power BI, Tableau, and SQL expertise. Responsibilities include building dashboards, ETL pipelines, and data warehouse management. Strong analytical skills required.",
     "tags": ["bi", "power bi", "tableau", "sql", "etl", "data warehouse"]},
    {"id": 22, "title": "Embedded Systems Engineer", "company": "HardwarePlus", "location": "Chittagong",
     "description": "Embedded systems engineer required with C and C++ programming experience. Knowledge of microcontrollers, RTOS, IoT, and hardware debugging tools. Experience with Arduino or Raspberry Pi preferred.",
     "tags": ["embedded", "c", "c++", "iot", "microcontroller", "rtos", "arduino"]},
    {"id": 23, "title": "Site Reliability Engineer", "company": "Uptime Inc", "location": "Remote",
     "description": "SRE needed to ensure system reliability, scalability, and performance. Skills: Linux, Python, Kubernetes, monitoring with Prometheus and Grafana, and incident management.",
     "tags": ["sre", "linux", "python", "kubernetes", "prometheus", "grafana"]},
    {"id": 24, "title": "Technical Content Writer", "company": "TechWrite", "location": "Remote",
     "description": "Technical writer needed to create documentation, tutorials, and blog posts for developer audiences. Strong writing skills and understanding of software development, APIs, and cloud technologies required.",
     "tags": ["writing", "documentation", "technical writing", "api", "content"]},
    {"id": 25, "title": "Computer Vision Engineer", "company": "VisionAI", "location": "Dhaka",
     "description": "Computer vision engineer required with expertise in OpenCV, deep learning, and image processing. Experience with YOLO, CNN models, and TensorFlow or PyTorch required. Python skills essential.",
     "tags": ["computer vision", "opencv", "deep learning", "yolo", "cnn", "python"]},
    {"id": 26, "title": "Scrum Master", "company": "AgilePro", "location": "Dhaka",
     "description": "Certified Scrum Master needed to facilitate agile ceremonies and coach development teams. Experience with JIRA, sprint planning, retrospectives, and stakeholder communication required.",
     "tags": ["scrum", "agile", "jira", "sprint", "project management"]},
    {"id": 27, "title": "Ruby on Rails Developer", "company": "RailsHub", "location": "Remote",
     "description": "Ruby on Rails developer needed with strong Ruby skills. Experience with MVC architecture, PostgreSQL, REST API development, and RSpec testing. Knowledge of Redis and Sidekiq preferred.",
     "tags": ["ruby", "rails", "postgresql", "rest", "rspec", "redis"]},
    {"id": 28, "title": "Systems Analyst", "company": "AnalyzeIT", "location": "Dhaka",
     "description": "Systems analyst required to analyze business requirements and design IT solutions. Skills needed: UML diagrams, SQL, requirement gathering, and process optimization. Communication skills essential.",
     "tags": ["systems analysis", "uml", "sql", "requirements", "business analysis"]},
    {"id": 29, "title": "AR/VR Developer", "company": "ImmerseTech", "location": "Dhaka",
     "description": "AR/VR developer needed with Unity, Unreal Engine, and C# or C++ skills. Experience developing immersive experiences for HoloLens, Oculus, or mobile AR using ARKit or ARCore.",
     "tags": ["ar", "vr", "unity", "unreal engine", "c#", "arkit", "arcore"]},
    {"id": 30, "title": "IT Support Specialist", "company": "HelpDesk Pro", "location": "Dhaka",
     "description": "IT support specialist needed for first and second-level technical support. Skills: Windows and Linux troubleshooting, networking basics, Active Directory, and ticketing systems like ServiceNow.",
     "tags": ["it support", "windows", "linux", "networking", "active directory", "helpdesk"]},
    {"id": 31, "title": "Data Engineer", "company": "PipelineWorks", "location": "Dhaka",
     "description": "Data engineer needed to build and maintain scalable data pipelines. Experience with Apache Spark, Kafka, Airflow, and cloud data warehouses like BigQuery or Redshift. Python and SQL skills required.",
     "tags": ["data engineering", "spark", "kafka", "airflow", "python", "sql", "bigquery"]},
    {"id": 32, "title": "Golang Backend Developer", "company": "GoTech", "location": "Remote",
     "description": "Backend developer with Go (Golang) experience needed. Must know concurrency patterns, RESTful API design, gRPC, and PostgreSQL. Experience with microservices and Docker containers is essential.",
     "tags": ["golang", "go", "backend", "grpc", "microservices", "docker", "postgresql"]},
    {"id": 33, "title": "Salesforce Developer", "company": "CRMPro", "location": "Dhaka",
     "description": "Salesforce developer with Apex, Visualforce, and Lightning Web Components experience. Knowledge of Salesforce CRM, SOQL, and integration with third-party APIs required.",
     "tags": ["salesforce", "apex", "lwc", "crm", "soql", "lightning"]},
    {"id": 34, "title": "WordPress Developer", "company": "WebPress BD", "location": "Dhaka",
     "description": "WordPress developer required to build and customize websites using themes, plugins, and custom PHP code. Knowledge of WooCommerce, SEO basics, and website performance optimization preferred.",
     "tags": ["wordpress", "php", "woocommerce", "css", "seo", "web"]},
    {"id": 35, "title": "Flutter Mobile Developer", "company": "CrossPlatform", "location": "Dhaka",
     "description": "Flutter developer needed to build cross-platform mobile apps for iOS and Android. Strong Dart programming skills required. Experience with Firebase, REST APIs, and state management like BLoC or Provider.",
     "tags": ["flutter", "dart", "mobile", "firebase", "ios", "android", "bloc"]},
    {"id": 36, "title": "Digital Marketing Specialist", "company": "GrowthHQ", "location": "Dhaka",
     "description": "Digital marketing specialist needed with experience in SEO, Google Ads, Facebook Ads, and email marketing. Proficiency in Google Analytics, content marketing strategy, and campaign management required.",
     "tags": ["digital marketing", "seo", "google ads", "facebook ads", "analytics", "content"]},
    {"id": 37, "title": "Data Visualization Analyst", "company": "ChartIQ", "location": "Remote",
     "description": "Data visualization analyst needed to build interactive dashboards using Tableau, Power BI, or D3.js. Must be able to communicate complex data insights clearly. SQL and Python proficiency required.",
     "tags": ["data visualization", "tableau", "power bi", "d3.js", "sql", "python"]},
    {"id": 38, "title": "SAP Consultant", "company": "EnterpriseSoft", "location": "Dhaka",
     "description": "SAP consultant needed with experience in SAP FICO, SAP MM, or SAP SD modules. Ability to configure and customize SAP ERP systems. Business process knowledge and ABAP programming skills preferred.",
     "tags": ["sap", "erp", "fico", "abap", "business process", "enterprise"]},
    {"id": 39, "title": "Robotics Engineer", "company": "RoboTech", "location": "Dhaka",
     "description": "Robotics engineer required with experience in ROS, Python, and C++. Knowledge of robot kinematics, path planning, and sensor integration. Experience with Arduino, Raspberry Pi, or industrial robots preferred.",
     "tags": ["robotics", "ros", "python", "c++", "automation", "arduino", "sensors"]},
    {"id": 40, "title": "Cloud Security Engineer", "company": "SafeCloud", "location": "Remote",
     "description": "Cloud security engineer needed to implement security best practices on AWS and Azure. Experience with IAM, encryption, security auditing, compliance frameworks, and vulnerability management required.",
     "tags": ["cloud security", "aws", "azure", "iam", "compliance", "encryption"]},
    {"id": 41, "title": "React Native Developer", "company": "NativeMobile", "location": "Remote",
     "description": "React Native developer needed to build cross-platform mobile apps. Strong JavaScript and React skills required. Experience with Redux, Firebase, native device APIs, and app store deployment preferred.",
     "tags": ["react native", "javascript", "mobile", "redux", "firebase", "android", "ios"]},
    {"id": 42, "title": "Ethical Hacker", "company": "PenTestPro", "location": "Remote",
     "description": "Ethical hacker needed to perform penetration testing and security assessments. Experience with Metasploit, Burp Suite, Nmap, and Kali Linux required. CEH or OSCP certification is a plus.",
     "tags": ["ethical hacking", "penetration testing", "metasploit", "kali linux", "oscp", "security"]},
    {"id": 43, "title": "PHP Laravel Developer", "company": "LaravelBD", "location": "Dhaka",
     "description": "PHP Laravel developer needed to build web applications. Strong knowledge of Laravel, MySQL, RESTful APIs, and MVC architecture. Familiarity with Vue.js or React for frontend integration preferred.",
     "tags": ["php", "laravel", "mysql", "rest", "backend", "vue", "react"]},
    {"id": 44, "title": "Tableau Developer", "company": "DashCraft", "location": "Dhaka",
     "description": "Tableau developer needed to design and maintain business intelligence dashboards. Strong SQL skills and experience connecting Tableau to various data sources. Data storytelling and presentation skills required.",
     "tags": ["tableau", "bi", "sql", "data visualization", "dashboard", "reporting"]},
    {"id": 45, "title": "Hardware Engineer", "company": "CircuitLabs", "location": "Chittagong",
     "description": "Hardware engineer needed with PCB design, circuit analysis, and FPGA programming experience. Knowledge of Altium Designer, VHDL, and hardware testing methodologies. Embedded C experience preferred.",
     "tags": ["hardware", "pcb", "fpga", "vhdl", "embedded", "altium", "circuit"]},
    {"id": 46, "title": "Deep Learning Researcher", "company": "NeuroLab", "location": "Dhaka",
     "description": "Deep learning researcher needed to develop novel neural network architectures. Strong background in mathematics, PyTorch or TensorFlow, and experience publishing research papers preferred.",
     "tags": ["deep learning", "neural networks", "pytorch", "tensorflow", "research", "python"]},
    {"id": 47, "title": "Angular Frontend Developer", "company": "NgSolutions", "location": "Dhaka",
     "description": "Angular developer needed to build enterprise web applications. Strong TypeScript and Angular skills required. Experience with RxJS, Angular Material, REST API integration, and unit testing with Jasmine.",
     "tags": ["angular", "typescript", "rxjs", "frontend", "javascript", "jasmine"]},
    {"id": 48, "title": "Technical Project Manager", "company": "BuildRight", "location": "Dhaka",
     "description": "Technical project manager needed to oversee software development projects. PMP or Prince2 certification preferred. Skills: risk management, budgeting, agile, stakeholder communication, and delivery planning.",
     "tags": ["project management", "pmp", "agile", "scrum", "risk management", "leadership"]},
    {"id": 49, "title": "MLOps Engineer", "company": "ModelOps", "location": "Remote",
     "description": "MLOps engineer needed to manage machine learning model deployment and monitoring pipelines. Experience with MLflow, Kubeflow, Docker, Kubernetes, and cloud platforms required.",
     "tags": ["mlops", "mlflow", "kubeflow", "docker", "kubernetes", "machine learning", "python"]},
    {"id": 50, "title": "Vue.js Developer", "company": "VueCraft", "location": "Remote",
     "description": "Vue.js developer required to build modern web applications. Strong JavaScript knowledge and experience with Vuex, Vue Router, REST APIs, and unit testing. Nuxt.js experience is a bonus.",
     "tags": ["vue", "vuex", "javascript", "nuxt", "frontend", "rest"]},
    {"id": 51, "title": "Business Analyst", "company": "BizLogic", "location": "Dhaka",
     "description": "Business analyst needed to bridge the gap between business needs and technical solutions. Skills: requirement gathering, process mapping, stakeholder interviews, use case writing, and SQL for data queries.",
     "tags": ["business analysis", "requirements", "sql", "process mapping", "uml", "communication"]},
    {"id": 52, "title": "ERP Implementation Specialist", "company": "ERPWise", "location": "Dhaka",
     "description": "ERP specialist needed to implement and customize ERP solutions. Experience with Oracle ERP, SAP, or Odoo required. Ability to train users and provide post-implementation support.",
     "tags": ["erp", "oracle", "sap", "odoo", "implementation", "training"]},
    {"id": 53, "title": "Cloud Data Engineer", "company": "CloudStream", "location": "Remote",
     "description": "Cloud data engineer needed to design data lake and warehouse solutions on AWS or GCP. Skills: Python, SQL, dbt, Spark, and orchestration tools like Airflow or Prefect.",
     "tags": ["cloud", "data engineering", "aws", "gcp", "dbt", "spark", "airflow"]},
    {"id": 54, "title": "IT Auditor", "company": "AuditSure", "location": "Dhaka",
     "description": "IT auditor needed to assess information systems risk, compliance, and controls. CISA certification preferred. Knowledge of ISO 27001, COBIT, and IT audit methodologies required.",
     "tags": ["it audit", "cisa", "iso 27001", "compliance", "risk", "governance"]},
    {"id": 55, "title": "Software Architect", "company": "ArchDesign", "location": "Dhaka",
     "description": "Software architect needed to design scalable and maintainable system architectures. Experience with microservices, event-driven architecture, domain-driven design, and cloud platforms required.",
     "tags": ["architecture", "microservices", "event-driven", "ddd", "cloud", "system design"]},
    {"id": 56, "title": "GIS Developer", "company": "MapTech BD", "location": "Dhaka",
     "description": "GIS developer needed to develop geospatial applications. Skills: ArcGIS, QGIS, PostGIS, Python, and web mapping with Leaflet or Mapbox. Experience with spatial data analysis preferred.",
     "tags": ["gis", "arcgis", "qgis", "postgis", "python", "leaflet", "geospatial"]},
    {"id": 57, "title": "Automation Test Engineer", "company": "TestBot", "location": "Remote",
     "description": "Automation test engineer needed to build test frameworks using Selenium, Cypress, or Playwright. Experience with CI/CD integration, API testing with Postman or RestAssured, and BDD frameworks like Cucumber.",
     "tags": ["automation testing", "selenium", "cypress", "playwright", "api testing", "bdd"]},
    {"id": 58, "title": "Hadoop Developer", "company": "BigDataBD", "location": "Dhaka",
     "description": "Hadoop developer needed with experience in MapReduce, HDFS, Hive, and Pig. Knowledge of Spark, HBase, and Kafka for real-time data processing. Java or Python programming skills required.",
     "tags": ["hadoop", "mapreduce", "hive", "spark", "hdfs", "bigdata", "java"]},
    {"id": 59, "title": "Penetration Tester", "company": "RedTeam BD", "location": "Dhaka",
     "description": "Penetration tester needed to identify vulnerabilities in web, mobile, and network systems. Tools: Burp Suite, Nessus, Metasploit, Wireshark. CEH or OSCP certification strongly preferred.",
     "tags": ["penetration testing", "security", "burp suite", "metasploit", "nessus", "oscp"]},
    {"id": 60, "title": "Drupal Developer", "company": "CMSPro", "location": "Remote",
     "description": "Drupal developer needed to build and maintain content management systems. Strong PHP and Drupal module development skills required. Experience with MySQL, RESTful APIs, and theming with Twig preferred.",
     "tags": ["drupal", "php", "cms", "mysql", "twig", "rest", "web"]},
    {"id": 61, "title": "Data Governance Analyst", "company": "DataTrust", "location": "Dhaka",
     "description": "Data governance analyst needed to implement data quality, lineage, and cataloging initiatives. Experience with Collibra, Alation, or Apache Atlas. SQL and data management best practices knowledge required.",
     "tags": ["data governance", "data quality", "collibra", "sql", "metadata", "compliance"]},
    {"id": 62, "title": "Scala Developer", "company": "FuncProg", "location": "Remote",
     "description": "Scala developer needed for big data and distributed systems work. Experience with Apache Spark, Akka, Play Framework, and functional programming concepts required. Java background is acceptable.",
     "tags": ["scala", "spark", "akka", "functional programming", "big data", "java"]},
    {"id": 63, "title": "Low Code Developer", "company": "AppQuick", "location": "Dhaka",
     "description": "Low-code developer needed with experience in OutSystems, Mendix, or Microsoft Power Apps. Ability to build business applications rapidly. Basic SQL and REST API knowledge preferred.",
     "tags": ["low code", "outsystems", "mendix", "power apps", "sql", "business apps"]},
    {"id": 64, "title": "Kubernetes Administrator", "company": "ContainerOps", "location": "Remote",
     "description": "Kubernetes administrator needed to manage and scale container orchestration clusters. Experience with Helm, service mesh like Istio, CI/CD pipelines, and monitoring with Prometheus and Grafana.",
     "tags": ["kubernetes", "helm", "istio", "docker", "devops", "prometheus", "grafana"]},
    {"id": 65, "title": "Quantum Computing Researcher", "company": "QuantumLab", "location": "Remote",
     "description": "Quantum computing researcher needed with background in quantum algorithms, linear algebra, and physics. Experience with Qiskit or Cirq and programming in Python. PhD or Masters in related field preferred.",
     "tags": ["quantum computing", "qiskit", "python", "algorithms", "research", "physics"]},
    {"id": 66, "title": "Marketing Data Analyst", "company": "AdMetrics", "location": "Dhaka",
     "description": "Marketing data analyst needed to measure campaign performance and ROI. Skills: Google Analytics, SQL, Excel, Python for data analysis, A/B testing, and dashboard creation in Tableau or Power BI.",
     "tags": ["marketing analytics", "google analytics", "sql", "python", "a/b testing", "tableau"]},
    {"id": 67, "title": "Rust Systems Developer", "company": "SystemsLab", "location": "Remote",
     "description": "Rust developer needed for systems programming and performance-critical applications. Experience with memory safety, concurrency, WebAssembly, and CLI tool development. C or C++ background is helpful.",
     "tags": ["rust", "systems programming", "webassembly", "concurrency", "performance", "cli"]},
    {"id": 68, "title": "Infrastructure Engineer", "company": "InfraStack", "location": "Remote",
     "description": "Infrastructure engineer needed to manage on-premise and cloud infrastructure. Skills: Terraform, Ansible, Linux server administration, AWS or Azure, and networking. Experience with monitoring tools preferred.",
     "tags": ["infrastructure", "terraform", "ansible", "linux", "aws", "azure", "devops"]},
    {"id": 69, "title": "COBOL Developer", "company": "BankSys", "location": "Dhaka",
     "description": "COBOL developer needed to maintain and modernize legacy banking systems. Experience with COBOL, JCL, DB2, and mainframe environments required. CICS and batch processing knowledge preferred.",
     "tags": ["cobol", "mainframe", "jcl", "db2", "banking", "legacy", "cics"]},
    {"id": 70, "title": "Database Developer", "company": "QueryCraft", "location": "Dhaka",
     "description": "Database developer needed to write complex queries, stored procedures, and database design. Strong skills in SQL Server, T-SQL, query optimization, indexing, and SSRS report creation required.",
     "tags": ["sql server", "t-sql", "database", "ssrs", "stored procedures", "sql"]},
    {"id": 71, "title": "AI Research Scientist", "company": "DeepMind BD", "location": "Dhaka",
     "description": "AI research scientist needed to advance the state of the art in machine learning. PhD preferred. Publications in NeurIPS, ICML, or ICLR required. Python, PyTorch, and strong math background essential.",
     "tags": ["ai research", "machine learning", "pytorch", "python", "research", "nlp"]},
    {"id": 72, "title": "Chatbot Developer", "company": "BotFactory", "location": "Remote",
     "description": "Chatbot developer needed to build conversational AI using Rasa, Dialogflow, or GPT APIs. Experience with NLP, intent detection, entity extraction, and backend API integration required.",
     "tags": ["chatbot", "rasa", "dialogflow", "nlp", "python", "conversational ai"]},
    {"id": 73, "title": "Odoo Developer", "company": "OdooHub", "location": "Dhaka",
     "description": "Odoo developer needed to customize and extend Odoo ERP modules. Python, XML, and PostgreSQL skills required. Experience with Odoo 14/15/16 and module development preferred.",
     "tags": ["odoo", "erp", "python", "postgresql", "xml", "module development"]},
    {"id": 74, "title": "Next.js Developer", "company": "SSRLab", "location": "Remote",
     "description": "Next.js developer needed for server-side rendering and static site generation projects. Strong React and JavaScript skills required. Experience with Tailwind CSS, REST APIs, and Vercel deployment preferred.",
     "tags": ["nextjs", "react", "javascript", "ssr", "tailwind", "vercel", "frontend"]},
    {"id": 75, "title": "Django REST Developer", "company": "APIForge", "location": "Dhaka",
     "description": "Django developer needed to build RESTful APIs using Django REST Framework. Python, PostgreSQL, and authentication (JWT/OAuth) knowledge required. Experience with Celery and Redis preferred.",
     "tags": ["django", "drf", "python", "postgresql", "rest", "jwt", "redis"]},
    {"id": 76, "title": "Power Platform Developer", "company": "MSApps", "location": "Dhaka",
     "description": "Microsoft Power Platform developer needed with Power Apps, Power Automate, and Power BI skills. Experience with SharePoint integration, Dataverse, and Microsoft 365 admin preferred.",
     "tags": ["power platform", "power apps", "power automate", "power bi", "sharepoint", "microsoft"]},
    {"id": 77, "title": "Elastic Stack Engineer", "company": "LogSearch", "location": "Remote",
     "description": "Elastic Stack engineer needed to build and maintain ELK (Elasticsearch, Logstash, Kibana) pipelines. Experience with log analysis, alerting, and performance tuning. Python or Bash scripting skills required.",
     "tags": ["elasticsearch", "elk", "kibana", "logstash", "logging", "python"]},
    {"id": 78, "title": "AIOps Engineer", "company": "IntelliOps", "location": "Remote",
     "description": "AIOps engineer needed to integrate AI capabilities into IT operations. Skills: Python, machine learning, monitoring tools (Dynatrace, Splunk), and DevOps practices. Anomaly detection experience preferred.",
     "tags": ["aiops", "python", "machine learning", "splunk", "monitoring", "devops"]},
    {"id": 79, "title": "Shopify Developer", "company": "eComBD", "location": "Dhaka",
     "description": "Shopify developer needed to build and customize e-commerce stores. Experience with Liquid templating, Shopify APIs, theme development, and app integration. JavaScript and CSS skills required.",
     "tags": ["shopify", "liquid", "ecommerce", "javascript", "css", "web"]},
    {"id": 80, "title": "IoT Solutions Engineer", "company": "SmartThings BD", "location": "Dhaka",
     "description": "IoT engineer needed to develop smart device solutions. Skills: MQTT, Python, C++, AWS IoT, Raspberry Pi, and embedded systems. Experience with sensor integration and real-time data required.",
     "tags": ["iot", "mqtt", "python", "c++", "aws", "raspberry pi", "embedded"]},
    {"id": 81, "title": "Financial Analyst", "company": "FinTech BD", "location": "Dhaka",
     "description": "Financial analyst needed to analyze financial data and build models. Skills: Excel, SQL, Python for finance, Power BI, and financial reporting. CFA or finance degree preferred.",
     "tags": ["finance", "excel", "sql", "python", "power bi", "financial modeling"]},
    {"id": 82, "title": "Magento Developer", "company": "CartWorks", "location": "Remote",
     "description": "Magento developer needed to build and customize e-commerce solutions. PHP, MySQL, and Magento 2 module development experience required. REST API and GraphQL knowledge preferred.",
     "tags": ["magento", "php", "ecommerce", "mysql", "graphql", "rest"]},
    {"id": 83, "title": "Apache Kafka Engineer", "company": "StreamFlow", "location": "Remote",
     "description": "Kafka engineer needed to design and maintain real-time event streaming systems. Experience with Kafka Streams, Schema Registry, Confluent Platform, and Java or Python required.",
     "tags": ["kafka", "streaming", "java", "python", "event-driven", "confluent"]},
    {"id": 84, "title": "Bioinformatics Engineer", "company": "GeneTech", "location": "Dhaka",
     "description": "Bioinformatics engineer needed to analyze genomic data. Skills: Python, R, BioPython, sequence alignment, and NGS data processing pipelines. Machine learning for genomics experience preferred.",
     "tags": ["bioinformatics", "python", "r", "genomics", "machine learning", "biopython"]},
    {"id": 85, "title": "Terraform Developer", "company": "IaC Solutions", "location": "Remote",
     "description": "Terraform developer needed to write and maintain Infrastructure as Code. Experience with AWS, Azure, or GCP provisioning, Terraform modules, and CI/CD pipeline integration required.",
     "tags": ["terraform", "iac", "aws", "azure", "devops", "cloud", "automation"]},
    {"id": 86, "title": "CRM Developer", "company": "ClientPro", "location": "Dhaka",
     "description": "CRM developer needed to customize and integrate CRM platforms. Experience with HubSpot, Zoho, or Dynamics 365. API integration, workflow automation, and SQL database skills required.",
     "tags": ["crm", "hubspot", "zoho", "dynamics", "api", "sql", "automation"]},
    {"id": 87, "title": "Apache Spark Developer", "company": "BigSpark", "location": "Remote",
     "description": "Spark developer needed to build large-scale data processing pipelines. Proficiency in PySpark or Scala, HDFS, Hive, and cloud storage integration. Knowledge of Delta Lake preferred.",
     "tags": ["spark", "pyspark", "scala", "hadoop", "bigdata", "delta lake", "python"]},
    {"id": 88, "title": "Perl Developer", "company": "LegacyCode BD", "location": "Dhaka",
     "description": "Perl developer needed to maintain legacy enterprise systems. Experience with Perl scripting, regular expressions, file processing, and database integration with DBI. Linux environment required.",
     "tags": ["perl", "scripting", "linux", "regex", "database", "legacy"]},
    {"id": 89, "title": "R Statistical Developer", "company": "StatAnalytics", "location": "Remote",
     "description": "R developer needed for statistical analysis and data visualization. Skills: R, ggplot2, dplyr, Shiny app development, and statistical modeling. Research background preferred.",
     "tags": ["r", "ggplot2", "statistics", "shiny", "data visualization", "research"]},
    {"id": 90, "title": "Prompt Engineer", "company": "AIPromptLab", "location": "Remote",
     "description": "Prompt engineer needed to design and optimize prompts for large language models. Experience with GPT-4, Claude, and Gemini. Knowledge of NLP, zero-shot and few-shot learning techniques preferred.",
     "tags": ["prompt engineering", "llm", "gpt", "nlp", "ai", "python"]},
    {"id": 91, "title": "Compliance Officer", "company": "ReguTech BD", "location": "Dhaka",
     "description": "Compliance officer needed to ensure regulatory adherence. Knowledge of GDPR, ISO standards, data privacy laws, and audit management. SQL for compliance reporting and risk assessment skills required.",
     "tags": ["compliance", "gdpr", "risk", "iso", "audit", "data privacy"]},
    {"id": 92, "title": "ETL Developer", "company": "DataMover", "location": "Dhaka",
     "description": "ETL developer needed to design and build data integration pipelines. Experience with SSIS, Talend, or Apache NiFi. SQL, Python scripting, and data warehouse knowledge required.",
     "tags": ["etl", "ssis", "talend", "nifi", "sql", "python", "data warehouse"]},
    {"id": 93, "title": "Conversational AI Developer", "company": "TalkBot BD", "location": "Dhaka",
     "description": "Conversational AI developer needed to build voice and text assistants. Experience with Amazon Lex, Google Dialogflow, or Microsoft Bot Framework. NLP and Python skills required.",
     "tags": ["conversational ai", "nlp", "dialogflow", "amazon lex", "python", "chatbot"]},
    {"id": 94, "title": "Mainframe Developer", "company": "CoreBank", "location": "Dhaka",
     "description": "Mainframe developer needed with IBM z/OS, COBOL, JCL, and VSAM experience. Knowledge of batch processing, CICS, and DB2 required. Banking or insurance domain knowledge preferred.",
     "tags": ["mainframe", "cobol", "jcl", "db2", "ibm", "banking", "cics"]},
    {"id": 95, "title": "Solr Search Engineer", "company": "SearchCraft", "location": "Remote",
     "description": "Solr search engineer needed to implement and optimize Apache Solr search solutions. Experience with schema design, query tuning, faceted search, and Java. Elasticsearch knowledge is a plus.",
     "tags": ["solr", "search", "java", "elasticsearch", "indexing", "information retrieval"]},
    {"id": 96, "title": "NoSQL Database Engineer", "company": "DocDB BD", "location": "Dhaka",
     "description": "NoSQL engineer needed with experience in MongoDB, Cassandra, and Redis. Knowledge of data modeling for document and column-family stores, performance tuning, and replication strategies.",
     "tags": ["nosql", "mongodb", "cassandra", "redis", "database", "performance"]},
    {"id": 97, "title": "Data Privacy Engineer", "company": "PrivacyFirst", "location": "Remote",
     "description": "Data privacy engineer needed to implement privacy-by-design principles. Skills: GDPR, CCPA compliance, data anonymization, encryption, and privacy impact assessments. Python or Java preferred.",
     "tags": ["data privacy", "gdpr", "ccpa", "encryption", "compliance", "python"]},
    {"id": 98, "title": "Digital Twin Engineer", "company": "TwinSim", "location": "Remote",
     "description": "Digital twin engineer needed to design simulation models for physical systems. Experience with IoT, Python, Azure Digital Twins, and 3D modeling. Knowledge of industrial IoT and real-time data preferred.",
     "tags": ["digital twin", "iot", "python", "azure", "simulation", "industrial"]},
    {"id": 99, "title": "API Integration Specialist", "company": "ConnectAPI", "location": "Dhaka",
     "description": "API integration specialist needed to connect third-party services. Strong knowledge of REST, GraphQL, OAuth, webhooks, and tools like Postman and MuleSoft. Python or JavaScript skills required.",
     "tags": ["api", "rest", "graphql", "oauth", "mulesoft", "python", "javascript"]},
    {"id": 100, "title": "AI Product Manager", "company": "AIFirst", "location": "Dhaka",
     "description": "AI product manager needed to lead the development of AI-powered products. Understanding of machine learning concepts, ability to define AI product roadmaps, user research, and collaboration with data science teams.",
     "tags": ["product management", "ai", "machine learning", "roadmap", "user research", "agile"]},
]


# ════════════════════════════════════════════════════════════
#  PREPROCESSING
# ════════════════════════════════════════════════════════════
def preprocess(text: str) -> list[str]:
    tokens = re.findall(r"[a-z]+", text.lower())
    return [stem(t) for t in tokens if t not in STOPWORDS and len(t) > 1]


# ════════════════════════════════════════════════════════════
#  INVERTED INDEX
# ════════════════════════════════════════════════════════════
class InvertedIndex:
    def __init__(self):
        self.index: dict = {}
        self.doc_lengths: dict = {}
        self.doc_count: int = 0

    def build(self, documents):
        for doc in documents:
            doc_id = doc["id"]
            text = doc["title"] + " " + doc["description"] + " " + " ".join(doc["tags"])
            tokens = preprocess(text)
            self.doc_lengths[doc_id] = len(tokens)
            self.doc_count += 1
            for pos, term in enumerate(tokens):
                self.index.setdefault(term, {})
                self.index[term].setdefault(doc_id, {"frequency": 0, "positions": []})
                self.index[term][doc_id]["frequency"] += 1
                self.index[term][doc_id]["positions"].append(pos)

    def get_postings(self, term):
        return self.index.get(term, {})

    def document_frequency(self, term):
        return len(self.index.get(term, {}))

    def stats(self):
        avg = sum(self.doc_lengths.values()) / len(self.doc_lengths) if self.doc_lengths else 0
        return {
            "total_documents": self.doc_count,
            "unique_terms": len(self.index),
            "avg_doc_length": round(avg, 2),
        }


# ════════════════════════════════════════════════════════════
#  QUERY PROCESSOR
# ════════════════════════════════════════════════════════════
class QueryProcessor:
    def __init__(self, index, documents):
        self.index = index
        self.docs = {doc["id"]: doc for doc in documents}

    def _tf(self, freq, doc_len):
        return freq / doc_len if doc_len else 0.0

    def _idf(self, term):
        df = self.index.document_frequency(term)
        if df == 0:
            return 0.0
        return math.log((self.index.doc_count + 1) / (df + 1)) + 1

    def _tfidf(self, term, doc_id):
        p = self.index.get_postings(term)
        if doc_id not in p:
            return 0.0
        return self._tf(p[doc_id]["frequency"], self.index.doc_lengths.get(doc_id, 1)) * self._idf(term)

    def _score(self, doc_id, terms):
        return sum(self._tfidf(t, doc_id) for t in terms)

    def _and_query(self, terms):
        if not terms:
            return set()
        result = set(self.index.get_postings(terms[0]).keys())
        for t in terms[1:]:
            result &= set(self.index.get_postings(t).keys())
        return result

    def _or_query(self, terms):
        result = set()
        for t in terms:
            result |= set(self.index.get_postings(t).keys())
        return result

    def _snippet(self, description, query, length=180):
        words = query.lower().split()
        dl = description.lower()
        best = 0
        for w in words:
            p = dl.find(w)
            if p != -1:
                best = max(0, p - 30)
                break
        snip = description[best: best + length]
        if best > 0:
            snip = "…" + snip
        if best + length < len(description):
            snip += "…"
        return snip

    def _highlight(self, text, query):
        words = query.split()
        for w in words:
            pattern = re.compile(re.escape(w), re.IGNORECASE)
            text = pattern.sub(f'<mark style="background:#fef08a;border-radius:2px;padding:0 2px">{w}</mark>', text)
        return text

    def search(self, query, mode="OR", top_k=10):
        terms = preprocess(query)
        if not terms:
            return []
        matching = self._and_query(terms) if mode.upper() == "AND" else self._or_query(terms)
        if not matching:
            return []
        scored = sorted(
            [(d, self._score(d, terms)) for d in matching],
            key=lambda x: x[1],
            reverse=True,
        )
        results = []
        for doc_id, score in scored[:top_k]:
            doc = self.docs[doc_id]
            snip = self._snippet(doc["description"], query)
            results.append({
                "rank": len(results) + 1,
                "id": doc_id,
                "title": doc["title"],
                "company": doc["company"],
                "location": doc["location"],
                "snippet": snip,
                "snippet_html": self._highlight(snip, query),
                "score": round(score, 4),
                "tags": doc["tags"],
            })
        return results


# ════════════════════════════════════════════════════════════
#  STREAMLIT APP
# ════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="JobSearch — Data Mining Lab",
    page_icon="🔍",
    layout="centered",
)

# ── Build index once and cache ───────────────────────────────
@st.cache_resource
def build_engine():
    idx = InvertedIndex()
    idx.build(JOB_LISTINGS)
    return QueryProcessor(idx, JOB_LISTINGS), idx


processor, index = build_engine()

# ── Custom CSS ───────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Product+Sans:wght@400;700&family=Roboto:wght@300;400;500&display=swap');

/* hide Streamlit chrome */
#MainMenu, header, footer {visibility: hidden;}
.block-container {padding-top: 1rem; max-width: 860px;}

/* logo area */
.logo-area {text-align: center; padding: 48px 0 24px;}
.logo-text {
    font-family: 'Roboto', sans-serif;
    font-size: 3.2rem;
    font-weight: 700;
    letter-spacing: -1px;
    user-select: none;
}
.logo-j {color: #4285F4;}
.logo-o {color: #EA4335;}
.logo-b {color: #FBBC05;}
.logo-s {color: #4285F4;}
.logo-e {color: #34A853;}
.logo-a {color: #EA4335;}
.logo-r {color: #4285F4;}
.logo-c {color: #FBBC05;}
.logo-h2{color: #34A853;}

.tagline {
    font-family: 'Roboto', sans-serif;
    font-size: 0.85rem;
    color: #888;
    margin-top: -8px;
    letter-spacing: 0.5px;
}

/* result card */
.result-card {
    border: 1px solid #e8eaed;
    border-radius: 10px;
    padding: 18px 22px;
    margin: 14px 0;
    background: #fff;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    transition: box-shadow 0.2s;
}
.result-card:hover {box-shadow: 0 3px 12px rgba(0,0,0,0.12);}

.result-rank {
    font-size: 0.72rem;
    color: #aaa;
    font-family: 'Roboto', sans-serif;
    margin-bottom: 2px;
}
.result-title {
    font-size: 1.15rem;
    font-weight: 600;
    color: #1a0dab;
    font-family: 'Roboto', sans-serif;
    margin-bottom: 2px;
}
.result-meta {
    font-size: 0.82rem;
    color: #006621;
    font-family: 'Roboto', sans-serif;
    margin-bottom: 6px;
}
.result-snippet {
    font-size: 0.88rem;
    color: #444;
    font-family: 'Roboto', sans-serif;
    line-height: 1.55;
    margin-bottom: 10px;
}
.result-score {
    font-size: 0.75rem;
    color: #888;
    font-family: monospace;
    margin-bottom: 8px;
}
.tag-pill {
    display: inline-block;
    background: #f1f3f4;
    color: #444;
    border-radius: 12px;
    padding: 2px 10px;
    font-size: 0.76rem;
    margin: 2px 2px 0 0;
    font-family: 'Roboto', sans-serif;
}

/* stats box */
.stat-box {
    background: #f8f9fa;
    border-radius: 8px;
    padding: 12px 16px;
    margin: 6px 0;
    font-family: 'Roboto', sans-serif;
    font-size: 0.88rem;
    color: #444;
}
.stat-label {font-weight: 500; color: #666; font-size: 0.78rem;}
.stat-value {font-size: 1.1rem; font-weight: 700; color: #1a73e8;}

/* no-results */
.no-results {text-align:center; padding: 40px; color:#888; font-family:'Roboto',sans-serif;}
</style>
""", unsafe_allow_html=True)

# ── Logo ─────────────────────────────────────────────────────
st.markdown("""
<div class="logo-area">
  <div class="logo-text">
    <span class="logo-j">J</span><span class="logo-o">o</span><span class="logo-b">b</span><span class="logo-s">S</span><span class="logo-e">e</span><span class="logo-a">a</span><span class="logo-r">r</span><span class="logo-c">c</span><span class="logo-h2">h</span>
  </div>
  <div class="tagline">Data Mining Lab &nbsp;·&nbsp; Inverted Index + TF-IDF &nbsp;·&nbsp; 100 Job Listings</div>
</div>
""", unsafe_allow_html=True)

# ── Search bar ───────────────────────────────────────────────
col_q, col_btn = st.columns([5, 1])
with col_q:
    query = st.text_input(
        label="search",
        placeholder='Try "python developer" or "cloud aws"',
        label_visibility="collapsed",
    )
with col_btn:
    search_clicked = st.button("Search 🔍", use_container_width=True)

# ── Options row ──────────────────────────────────────────────
c1, c2, c3 = st.columns([2, 2, 3])
with c1:
    mode = st.radio("Query mode", ["OR", "AND"], horizontal=True)
with c2:
    top_k = st.slider("Top K", min_value=1, max_value=20, value=5)
with c3:
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    loc_filter = st.selectbox(
        "Filter by location",
        ["All"] + sorted({d["location"] for d in JOB_LISTINGS}),
    )

st.divider()

# ── Sidebar — index stats ─────────────────────────────────────
with st.sidebar:
    st.markdown("### 📊 Index Statistics")
    s = index.stats()
    for label, val in [
        ("Total Documents", s["total_documents"]),
        ("Unique Terms", s["unique_terms"]),
        ("Avg Doc Length", f"{s['avg_doc_length']} tokens"),
    ]:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-label">{label}</div>
            <div class="stat-value">{val}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### 💡 Try these queries")
    EXAMPLES = [
        "python developer",
        "machine learning",
        "cloud aws kubernetes",
        "android mobile",
        "data remote",
        "security penetration",
        "react typescript",
        "nlp transformer",
    ]
    for ex in EXAMPLES:
        if st.button(ex, key=f"ex_{ex}", use_container_width=True):
            query = ex
            search_clicked = True

    st.markdown("---")
    st.markdown("""
    <small style='color:#aaa; font-family:Roboto,sans-serif;'>
    <b>How it works</b><br>
    Custom inverted index · Porter stemming · TF-IDF ranking ·
    Boolean AND/OR retrieval · No external search libraries
    </small>
    """, unsafe_allow_html=True)

# ── Results ──────────────────────────────────────────────────
if query and (search_clicked or query):
    results = processor.search(query, mode=mode, top_k=top_k)

    # Location filter
    if loc_filter != "All":
        results = [r for r in results if
                   index.index and
                   next((d["location"] for d in JOB_LISTINGS if d["id"] == r["id"]), "") == loc_filter]

    if not results:
        st.markdown(f"""
        <div class="no-results">
            <div style="font-size:2rem">🔍</div>
            <div style="font-size:1rem;margin-top:8px">No results found for <b>"{query}"</b> in <b>{mode}</b> mode.</div>
            <div style="font-size:0.85rem;margin-top:6px;color:#aaa">
                Try switching to <b>OR</b> mode, or use different keywords.
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(
            f'<div style="font-size:0.85rem;color:#666;font-family:Roboto,sans-serif;margin-bottom:8px">'
            f'About <b>{len(results)}</b> result(s) for <b>"{query}"</b> &nbsp;·&nbsp; Mode: <b>{mode}</b>'
            f'</div>',
            unsafe_allow_html=True,
        )
        for r in results:
            tags_html = "".join(f'<span class="tag-pill">{t}</span>' for t in r["tags"])
            loc_icon = "🏠" if r["location"] == "Remote" else "📍"
            card_html = f"""
            <div class="result-card">
                <div class="result-rank">#{r['rank']} &nbsp;·&nbsp; Score: {r['score']}</div>
                <div class="result-title">{r['title']}</div>
                <div class="result-meta">{r['company']} &nbsp;·&nbsp; {loc_icon} {r['location']}</div>
                <div class="result-snippet">{r['snippet_html']}</div>
                <div>{tags_html}</div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
elif not query:
    # Landing state suggestions
    st.markdown("""
    <div style="text-align:center;padding:20px 0;font-family:Roboto,sans-serif;color:#888">
        Enter a keyword above to search 100 tech job listings.<br>
        <small>Supports single keywords, multi-word queries, AND/OR boolean modes.</small>
    </div>
    """, unsafe_allow_html=True)
