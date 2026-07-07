import asyncio
import json
import hashlib
import os
import sys

# Ensure backend root is in system path so 'app' imports work correctly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db import db
from app.prisma_client import Json

def hash_password(password: str) -> str:
    salt = os.urandom(16)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return f"{salt.hex()}:{key.hex()}"

async def seed():
    print("Connecting to database...")
    await db.connect()

    print("Cleaning database...")
    await db.userprogress.delete_many()
    await db.userexamattempt.delete_many()
    await db.lesson.delete_many()
    await db.course.delete_many()
    await db.question.delete_many()
    await db.user.delete_many()

    print("Seeding Users...")
    hashed_password = hash_password("user123")
    hashed_admin_password = hash_password("admin123")

    # Regular Free User
    free_user = await db.user.create(
        data={
            "email": "free@gordon.com",
            "passwordHash": hashed_password,
            "membershipLevel": "free"
        }
    )

    # Regular Premium User
    premium_user = await db.user.create(
        data={
            "email": "premium@gordon.com",
            "passwordHash": hashed_password,
            "membershipLevel": "premium"
        }
    )

    # Admin User
    admin_user = await db.user.create(
        data={
            "email": "admin@gordon.com",
            "passwordHash": hashed_admin_password,
            "membershipLevel": "premium"
        }
    )

    # Social Google User (Seeded dummy)
    google_user = await db.user.create(
        data={
            "email": "testgoogleuser@example.com",
            "googleId": "1234567890",
            "membershipLevel": "free"
        }
    )

    print("Seeding Courses & Lessons...")
    # Cloudinary sample videos or dummy video links
    video_1 = "https://res.cloudinary.com/demo/video/upload/sp_auto/dog.mp4"
    video_2 = "https://res.cloudinary.com/demo/video/upload/v1502283084/sea.mp4"
    video_3 = "https://res.cloudinary.com/demo/video/upload/v1612345678/sample.mp4"

    ccna = await db.course.create(
        data={
            "title": "CCNA 200-301 Complete Course",
            "description": "Master Cisco networking basics, routing, switching, and security protocols.",
            "thumbnailUrl": "https://images.unsplash.com/photo-1544197150-b99a580bb7a8?w=500",
            "difficulty": "Beginner"
        }
    )

    await db.lesson.create_many(
        data=[
            {
                "courseId": ccna.id,
                "title": "Introduction to Cisco CCNA 200-301",
                "videoUrl": video_1,
                "textContent": "Welcome to the CCNA course! In this lesson, we will cover the networking models, OSI, and TCP/IP protocol suites.",
                "orderIndex": 1
            },
            {
                "courseId": ccna.id,
                "title": "Understanding IPv4 Addressing & Subnetting",
                "videoUrl": video_2,
                "textContent": "Subnetting is the process of dividing a network into smaller sub-networks. We will cover CIDR notation, subnet masks, and broadcast domains.",
                "orderIndex": 2
            },
            {
                "courseId": ccna.id,
                "title": "Routing Protocols: OSPF & Static Routes",
                "videoUrl": video_3,
                "textContent": "Learn how routers forward packets. We will configure static routes and dynamic routing using Open Shortest Path First (OSPF).",
                "orderIndex": 3
            }
        ]
    )

    ccnp = await db.course.create(
        data={
            "title": "CCNP Enterprise ENCOR (350-401)",
            "description": "Advanced enterprise routing, switching, wireless, SD-WAN, and network automation.",
            "thumbnailUrl": "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=500",
            "difficulty": "Advanced"
        }
    )

    await db.lesson.create_many(
        data=[
            {
                "courseId": ccnp.id,
                "title": "Enterprise Network Architecture",
                "videoUrl": video_1,
                "textContent": "Analyze enterprise architecture designs, hierarchical layouts, high availability, and redundancy protocols like HSRP/VRRP.",
                "orderIndex": 1
            },
            {
                "courseId": ccnp.id,
                "title": "Deep Dive into BGP (Border Gateway Protocol)",
                "videoUrl": video_2,
                "textContent": "Explore eBGP, iBGP, path vector attributes, route reflection, and routing policies for enterprise scale.",
                "orderIndex": 2
            }
        ]
    )

    cyber = await db.course.create(
        data={
            "title": "Introduction to Cybersecurity Fundamentals",
            "description": "Learn the basics of cybersecurity, cryptography, risk management, and malware analysis.",
            "thumbnailUrl": "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=500",
            "difficulty": "Intermediate"
        }
    )

    await db.lesson.create_many(
        data=[
            {
                "courseId": cyber.id,
                "title": "Cybersecurity Threats & Vulnerabilities",
                "videoUrl": video_3,
                "textContent": "Understand threat actors, social engineering, malware categories (ransomware, trojans), and scanning networks for vulnerability.",
                "orderIndex": 1
            }
        ]
    )

    print("Seeding Questions (50 questions)...")
    questions_data = []

    # Generate 50 questions across categories
    categories = ["CCNA", "CCNP", "Cybersecurity", "Networking"]
    for i in range(1, 51):
        cat = categories[(i - 1) % len(categories)]
        
        # Specific networking quiz question details
        q_text = f"[{cat}] Question #{i}: What is the primary function of protocol or device at index #{i}?"
        options = [
            f"Option A: To forward frames at Layer 2 for item #{i}",
            f"Option B: To route packets at Layer 3 for item #{i}",
            f"Option C: To enforce security rules at Layer 4-7 for item #{i}",
            f"Option D: None of the above options fit item #{i}"
        ]
        
        correct = "B" if i % 2 == 0 else "A"
        explanation = f"This is the detailed explanation for question #{i} under category {cat}. The correct choice is Option {correct} because of routing/switching principles."

        questions_data.append({
            "category": cat,
            "questionText": q_text,
            "options": json.dumps(options),
            "correctOption": correct,
            "explanation": explanation,
            "indexNumber": i
        })

    # Bulk insert
    for q_item in questions_data:
        q_item["options"] = Json(json.loads(q_item["options"]))
        await db.question.create(data=q_item)

    print("Database seeding completed successfully!")
    await db.disconnect()

if __name__ == "__main__":
    asyncio.run(seed())
