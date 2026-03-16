#!/usr/bin/env python3
from pathlib import Path

from weasyprint import HTML

PROJECT_ROOT = Path(__file__).resolve().parent.parent

CLOUD_ENGINEER_PATH = (
    PROJECT_ROOT / "hand_crafted_resumes" / "Robin Codewright - Cloud Engineer (example).pdf"
)
FULL_STACK_PATH = (
    PROJECT_ROOT / "hand_crafted_resumes" / "Robin Codewright - Full Stack Developer (example).pdf"
)
JD_PATH = (
    PROJECT_ROOT
    / "data"
    / "jobs"
    / "example"
    / "senior-cloud-platform-engineer"
    / "Senior Cloud Platform Engineer - Stellarpath Industries (example).pdf"
)


RESUME_CSS = """
body {
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    font-size: 10.5pt;
    line-height: 1.4;
    color: #333;
    margin: 0;
    padding: 0;
}
@page {
    size: letter;
    margin: 0.7in 0.8in;
}
h1 {
    font-size: 20pt;
    margin: 0 0 2pt 0;
    color: #111;
}
.contact {
    font-size: 9.5pt;
    color: #555;
    margin-bottom: 12pt;
}
.contact a { color: #555; text-decoration: none; }
h2 {
    font-size: 11.5pt;
    text-transform: uppercase;
    letter-spacing: 1px;
    border-bottom: 1px solid #999;
    padding-bottom: 2pt;
    margin: 14pt 0 6pt 0;
    color: #222;
}
.job-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 2pt;
}
.job-title { font-weight: bold; font-size: 10.5pt; }
.job-dates { font-size: 10pt; color: #555; }
.job-company { font-style: italic; font-size: 10pt; margin-bottom: 4pt; }
ul {
    margin: 2pt 0 8pt 0;
    padding-left: 18pt;
}
li { margin-bottom: 2pt; }
.skills-row { margin-bottom: 2pt; }
.skills-label { font-weight: bold; }
"""

JD_CSS = """
body {
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    font-size: 10.5pt;
    line-height: 1.5;
    color: #333;
    margin: 0;
    padding: 0;
}
@page {
    size: letter;
    margin: 0.8in 0.9in;
}
h1 {
    font-size: 18pt;
    margin: 0 0 4pt 0;
    color: #111;
}
.company-name {
    font-size: 13pt;
    color: #444;
    margin-bottom: 14pt;
}
h2 {
    font-size: 11.5pt;
    margin: 16pt 0 6pt 0;
    color: #222;
}
ul {
    margin: 4pt 0 8pt 0;
    padding-left: 20pt;
}
li { margin-bottom: 3pt; }
p { margin: 4pt 0; }
.meta {
    font-size: 9.5pt;
    color: #666;
    border-top: 1px solid #ccc;
    margin-top: 20pt;
    padding-top: 8pt;
}
"""

CONTACT_HTML = """
<h1>Robin Codewright</h1>
<div class="contact">
Portland, OR &middot; robin@example.com &middot; 555.123.4567<br>
<a href="https://github.com/robincodewright">github.com/robincodewright</a> &middot;
<a href="https://linkedin.com/in/robincodewright">linkedin.com/in/robincodewright</a>
</div>
"""

EDUCATION_HTML = """
<h2>Education</h2>
<div class="job-header">
    <span class="job-title">M.S. Computer Science</span>
    <span class="job-dates">2013</span>
</div>
<div class="job-company">Cascadia University</div>
<div class="job-header" style="margin-top: 6pt;">
    <span class="job-title">B.S. Computer Science</span>
    <span class="job-dates">2011</span>
</div>
<div class="job-company">Cascadia University</div>
"""


def build_cloud_engineer_html():
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>{RESUME_CSS}</style></head><body>

{CONTACT_HTML}

<h2>Experience</h2>

<div class="job-header">
    <span class="job-title">Senior Software Engineer</span>
    <span class="job-dates">Jan 2023 &ndash; Present</span>
</div>
<div class="job-company">Nimbus Labs &mdash; Cloud infrastructure startup building developer tools for multi-cloud deployments</div>
<ul>
    <li>Led migration of monolithic API to event-driven microservices using Go and NATS, reducing p99 latency by 40%</li>
    <li>Designed and implemented Terraform provider for proprietary cloud orchestration layer</li>
    <li>Built real-time cost anomaly detection pipeline using Kafka Streams and PostgreSQL</li>
    <li>Mentored team of four junior engineers through architecture reviews and pair programming sessions</li>
    <li>Established automated load testing framework with k6 integrated into CI/CD pipeline</li>
    <li>Implemented distributed tracing across 12 microservices using OpenTelemetry and Jaeger</li>
</ul>

<div class="job-header">
    <span class="job-title">Software Engineer</span>
    <span class="job-dates">Mar 2021 &ndash; Jan 2023</span>
</div>
<div class="job-company">Nimbus Labs</div>
<ul>
    <li>Developed REST API gateway handling 50k requests per second using Go and Redis</li>
    <li>Created CLI tool for infrastructure provisioning adopted by 200+ enterprise customers</li>
    <li>Built webhook delivery system with at-least-once guarantees using PostgreSQL and background workers</li>
    <li>Wrote comprehensive integration test suite covering multi-cloud provisioning workflows</li>
</ul>

<div class="job-header">
    <span class="job-title">Backend Engineer</span>
    <span class="job-dates">Jun 2019 &ndash; Mar 2021</span>
</div>
<div class="job-company">Verdant Systems &mdash; IoT platform connecting industrial sensors to cloud analytics dashboards</div>
<ul>
    <li>Designed MQTT broker integration processing 100k sensor messages per minute into TimescaleDB</li>
    <li>Implemented role-based access control system supporting multi-tenant device hierarchies</li>
    <li>Created Python SDK for third-party developers to integrate with sensor data streams</li>
    <li>Optimized time-series query engine reducing dashboard load times from 8 seconds to under 500ms</li>
    <li>Deployed Kubernetes-based staging environment with automated database seeding from production snapshots</li>
</ul>

<h2>Skills</h2>
<div class="skills-row"><span class="skills-label">Languages:</span> Go, Python, SQL, Bash</div>
<div class="skills-row"><span class="skills-label">Cloud &amp; Infrastructure:</span> AWS, Terraform, Kubernetes, Docker, Linux, NATS, Kafka</div>
<div class="skills-row"><span class="skills-label">Data:</span> PostgreSQL, TimescaleDB, Redis</div>
<div class="skills-row"><span class="skills-label">Observability:</span> OpenTelemetry, Jaeger, Grafana, k6</div>

{EDUCATION_HTML}

<h2>Publications</h2>
<p>"Scaling Event-Driven Architectures: Patterns for Multi-Cloud Message Routing" &mdash;
International Conference on Distributed Systems (ICDS), March 2024</p>

</body></html>"""


def build_full_stack_html():
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>{RESUME_CSS}</style></head><body>

{CONTACT_HTML}

<h2>Experience</h2>

<div class="job-header">
    <span class="job-title">Full Stack Developer</span>
    <span class="job-dates">Sep 2017 &ndash; Jun 2019</span>
</div>
<div class="job-company">Pixelweave &mdash; Digital agency building custom web applications for e-commerce and media clients</div>
<ul>
    <li>Developed React component library used across 15 client projects, reducing frontend development time by 30%</li>
    <li>Built Node.js payment processing service integrating Stripe and PayPal for e-commerce platform</li>
    <li>Implemented server-side rendering pipeline with Next.js improving SEO scores by 60 points</li>
    <li>Created automated visual regression testing system using Puppeteer and Percy</li>
    <li>Migrated legacy jQuery applications to React with zero downtime using incremental adoption strategy</li>
</ul>

<div class="job-header">
    <span class="job-title">Software Engineer</span>
    <span class="job-dates">Aug 2015 &ndash; Sep 2017</span>
</div>
<div class="job-company">DataForge Inc &mdash; Data engineering consultancy building ETL pipelines and analytics platforms</div>
<ul>
    <li>Built Apache Spark pipelines processing 2TB of daily transaction data for financial reporting</li>
    <li>Designed data warehouse schema supporting real-time and batch analytics on AWS Redshift</li>
    <li>Developed Airflow DAGs orchestrating 40+ ETL jobs with dependency management and alerting</li>
    <li>Created data quality validation framework catching schema drift before pipeline failures</li>
    <li>Wrote Python client library for internal data catalog API used by 50+ analysts</li>
</ul>

<div class="job-header">
    <span class="job-title">Junior Developer</span>
    <span class="job-dates">Jun 2013 &ndash; Aug 2015</span>
</div>
<div class="job-company">Ironclad Software &mdash; Enterprise software company providing document management and workflow automation</div>
<ul>
    <li>Developed RESTful API endpoints for document versioning system serving 500 concurrent users</li>
    <li>Implemented full-text search functionality using Elasticsearch across 10M+ document repository</li>
    <li>Built automated deployment pipeline using Jenkins reducing release cycle from 2 weeks to 2 days</li>
    <li>Wrote unit and integration tests achieving 85% code coverage on document processing module</li>
</ul>

<h2>Skills</h2>
<div class="skills-row"><span class="skills-label">Languages:</span> JavaScript, TypeScript, Python, Java, SQL</div>
<div class="skills-row"><span class="skills-label">Web:</span> React, Next.js, Node.js, HTML/CSS</div>
<div class="skills-row"><span class="skills-label">Data:</span> PostgreSQL, Elasticsearch, Apache Spark, Airflow, AWS Redshift</div>
<div class="skills-row"><span class="skills-label">DevOps:</span> Jenkins, CI/CD, Docker</div>

{EDUCATION_HTML}

</body></html>"""


def build_jd_html():
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>{JD_CSS}</style></head><body>

<h1>Senior Cloud Platform Engineer</h1>
<div class="company-name">Stellarpath Industries &mdash; Portland, OR (Hybrid)</div>

<p>Stellarpath Industries processes petabytes of satellite imagery and telemetry data for
commercial and government clients. Our cloud platform team builds the infrastructure
that ingests, processes, and serves this data at scale. We're looking for a senior
engineer to help us design and operate the next generation of our platform services.</p>

<h2>I. Summary</h2>
<p>You will own critical pieces of our cloud infrastructure — from data ingestion pipelines
to the APIs that serve processed imagery to downstream consumers. This is a hands-on role:
you'll write Go services, manage Terraform configurations, and be on-call for the systems
you build. You'll work closely with data scientists, ML engineers, and product teams to
deliver reliable, cost-effective infrastructure for satellite data processing.</p>

<h2>II. Responsibilities</h2>
<ul>
    <li>Design, build, and maintain Go microservices for satellite data ingestion and processing pipelines</li>
    <li>Own and evolve our AWS infrastructure using Terraform, including EKS clusters, networking, and IAM policies</li>
    <li>Build and maintain RESTful and gRPC APIs for internal and external consumers of processed satellite data</li>
    <li>Implement observability across platform services using OpenTelemetry, Prometheus, and Grafana</li>
    <li>Design and operate CI/CD pipelines for platform services with automated testing and canary deployments</li>
    <li>Collaborate with data science and ML teams to optimize compute resource allocation for processing workloads</li>
    <li>Participate in architecture reviews and contribute to technical design documents</li>
    <li>Mentor junior engineers and contribute to team engineering standards</li>
</ul>

<h2>III. Required Skills</h2>
<ul>
    <li>Strong proficiency in Go for building production services</li>
    <li>Python for scripting, tooling, and data pipeline integration</li>
    <li>Deep experience with AWS (EKS, EC2, S3, IAM, VPC, Lambda)</li>
    <li>Infrastructure as code with Terraform (modules, state management, CI integration)</li>
    <li>Container orchestration with Kubernetes (deployment strategies, resource management, networking)</li>
    <li>Relational database design and optimization (PostgreSQL)</li>
    <li>API design principles (REST, gRPC, versioning, authentication)</li>
    <li>Distributed systems concepts (consistency, partitioning, failure modes)</li>
    <li>Strong communication skills and ability to work across teams</li>
</ul>

<h2>IV. Desired Skills</h2>
<ul>
    <li>Experience with message brokers (Kafka, NATS) for event-driven architectures</li>
    <li>Familiarity with OpenTelemetry and distributed tracing</li>
    <li>Experience with time-series data storage and querying</li>
    <li>Geospatial data formats and processing (GeoTIFF, COG, STAC)</li>
    <li>Cost optimization strategies for large-scale cloud workloads</li>
    <li>Experience mentoring engineers or leading technical initiatives</li>
</ul>

<h2>V. Education</h2>
<ul>
    <li>B.S. in Computer Science, Software Engineering, or related field (required)</li>
    <li>M.S. in Computer Science or related field (preferred)</li>
</ul>

<h2>VI. Role Flexibility</h2>
<p>This is a hybrid position based in our Portland, OR office (3 days/week in-office).
Occasional travel to our satellite ground station facilities may be required (2&ndash;3 times per year).</p>

<h2>VII. Years of Experience</h2>
<p>5+ years of professional software engineering experience, with at least 3 years focused on
cloud infrastructure or platform engineering.</p>

<div class="meta">
Stellarpath Industries is an equal opportunity employer. We celebrate diversity and are committed to
creating an inclusive environment for all employees.<br><br>
Stellarpath Industries &middot; Portland, OR &middot; stellarpath.example.com
</div>

</body></html>"""


def generate_pdf(html_content, output_path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc = HTML(string=html_content).render()
    doc.write_pdf(output_path)
    return len(doc.pages)


def main():
    files = [
        (CLOUD_ENGINEER_PATH, build_cloud_engineer_html),
        (FULL_STACK_PATH, build_full_stack_html),
        (JD_PATH, build_jd_html),
    ]

    for path, builder in files:
        html = builder()
        pages = generate_pdf(html, path)
        print(
            f"Generated: {path.relative_to(PROJECT_ROOT)} ({pages} page{'s' if pages != 1 else ''})"
        )


if __name__ == "__main__":
    main()
