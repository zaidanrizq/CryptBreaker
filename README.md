# CryptBreaker

CryptBreaker is a hash password brute-forcing tool created using Python, designed to efficiently break hash passwords through distributed computing. The project leverages a distributed system architecture utilizing RabbitMQ to implement the producer-consumer model, allowing tasks to be spread across multiple nodes for faster and more scalable password cracking.

This project is developed as a capstone project for the subject "Sistem Terdistribusi dan Paralel" (Distributed and Parallel Systems) in the fifth semester of the Informatics program.

## Features

- **Distributed Brute-Force Attack**: Distributes the brute-force workload across multiple workers to speed up the password-cracking process.
- **RabbitMQ Integration**: Utilizes RabbitMQ for message queuing, allowing for efficient communication between the producer (task generator) and consumers (worker nodes).
- **Scalability**: Easily scalable by adding more worker nodes to handle increased workloads.
- **Modular Design**: Built with modularity in mind, allowing easy extension and modification of the brute-force algorithm and the hashing functions.
- **Python-based Implementation**: Developed entirely in Python, making it accessible and easy to modify for educational and research purposes.

## Components

1. **Producer**: Generates hash passwords and places tasks in the RabbitMQ queue for processing by consumers.
2. **Consumers (Workers)**: Multiple consumer nodes listen to the RabbitMQ queue, retrieve tasks, and attempt to brute-force the hash passwords. Each worker operates independently, allowing for parallel processing.
3. **RabbitMQ Server**: Acts as the central message broker, coordinating communication between producers and consumers.

## Installation

To set up and run CryptBreaker, follow these steps:

1. **Install RabbitMQ**: Make sure you have RabbitMQ installed and running on your system. You can download it from the official [RabbitMQ website](https://www.rabbitmq.com/download.html).

2. **Clone the Repository**:

   ```bash
   git clone https://github.com/your-username/CryptBreaker.git
   cd CryptBreaker
