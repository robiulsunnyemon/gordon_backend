import asyncio
import os
import sys

# Add the parent directory to sys.path so 'app' can be found
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.db import db
from prisma import Prisma

# Sample Interview Questions Data
INTERVIEW_QUESTIONS = [
    {
        "topic": "CCNA",
        "questionText": "What is the primary purpose of OSPF (Open Shortest Path First)?",
        "correctAnswer": "OSPF is a link-state routing protocol used to find the best path for routing IP packets across a single IP network. It calculates the shortest path tree using Dijkstra's algorithm and maintains a topological map of the network."
    },
    {
        "topic": "CCNA",
        "questionText": "What is a VLAN and why is it used?",
        "correctAnswer": "A VLAN (Virtual LAN) is a logical grouping of devices on a network that act as if they are attached to the same broadcast domain, regardless of their physical location. VLANs are used to improve network security, manage broadcast traffic, and simplify network management."
    },
    {
        "topic": "Networking",
        "questionText": "Explain the main difference between TCP and UDP.",
        "correctAnswer": "TCP (Transmission Control Protocol) is connection-oriented, meaning it establishes a reliable connection and ensures that data packets are delivered in order without errors. UDP (User Datagram Protocol) is connectionless, meaning it sends packets without checking for delivery, making it faster but less reliable."
    },
    {
        "topic": "CCNA",
        "questionText": "What is a Default Gateway?",
        "correctAnswer": "A Default Gateway is a routing device (usually a router) used to forward all IP packets that are destined for an IP address outside of the local network/subnet."
    },
    {
        "topic": "Security",
        "questionText": "What is the difference between a Firewall and an Intrusion Prevention System (IPS)?",
        "correctAnswer": "A Firewall primarily relies on static rules to block or allow traffic based on ports and IP addresses. An IPS actively analyzes network traffic flows to detect and automatically prevent vulnerability exploits and malicious activity."
    }
]

async def seed_interviews():
    print("Connecting to the database...")
    if not db.is_connected():
        await db.connect()
    
    print("Clearing existing interview questions...")
    await db.interviewquestion.delete_many()

    print(f"Seeding {len(INTERVIEW_QUESTIONS)} interview questions...")
    for q in INTERVIEW_QUESTIONS:
        await db.interviewquestion.create(data=q)
        print(f"Created question: {q['questionText'][:30]}...")

    print("Seed completed successfully!")
    await db.disconnect()

if __name__ == "__main__":
    asyncio.run(seed_interviews())
