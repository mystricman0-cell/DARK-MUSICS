"""
RONALDO MUSIC - MongoDB Cleanup Script
Run this to clean all junk/old data from MongoDB.
Usage: python3 mongo_cleanup.py
"""

import asyncio
from os import getenv

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

MONGO_URI = getenv("MONGO_DB_URI")
if not MONGO_URI:
    print("[ERROR] MONGO_DB_URI not set in environment!")
    exit(1)


async def cleanup():
    client = AsyncIOMotorClient(MONGO_URI)
    db = client.RONALDO_MUSIC

    print("=" * 50)
    print("  RONALDO MUSIC - MongoDB Cleanup")
    print("=" * 50)

    collections = await db.list_collection_names()
    print(f"\n[INFO] Found {len(collections)} collections: {collections}\n")

    total_deleted = 0

    # 1. Clean active chats (voice chats that are no longer active)
    if "activechats" in collections:
        result = await db.activechats.delete_many({})
        print(f"[CLEAN] Active Chats: {result.deleted_count} records deleted")
        total_deleted += result.deleted_count

    # 2. Clean active video chats
    if "activevideochats" in collections:
        result = await db.activevideochats.delete_many({})
        print(f"[CLEAN] Active Video Chats: {result.deleted_count} records deleted")
        total_deleted += result.deleted_count

    # 3. Clean download cache / queue
    if "queues" in collections:
        result = await db.queues.delete_many({})
        print(f"[CLEAN] Queues: {result.deleted_count} records deleted")
        total_deleted += result.deleted_count

    # 4. Clean served chats (optional - removes chat history)
    choice = input("\n[?] Delete served chats log? (y/N): ").strip().lower()
    if choice == "y":
        if "served_chats" in collections:
            result = await db.served_chats.delete_many({})
            print(f"[CLEAN] Served Chats: {result.deleted_count} records deleted")
            total_deleted += result.deleted_count
        if "served_users" in collections:
            result = await db.served_users.delete_many({})
            print(f"[CLEAN] Served Users: {result.deleted_count} records deleted")
            total_deleted += result.deleted_count

    # 5. Clean blocked users (optional)
    choice2 = input("[?] Reset banned/blocked users list? (y/N): ").strip().lower()
    if choice2 == "y":
        if "gban" in collections:
            result = await db.gban.delete_many({})
            print(f"[CLEAN] GBanned Users: {result.deleted_count} records deleted")
            total_deleted += result.deleted_count
        if "banned_users" in collections:
            result = await db.banned_users.delete_many({})
            print(f"[CLEAN] Banned Users: {result.deleted_count} records deleted")
            total_deleted += result.deleted_count
        if "blocked_chats" in collections:
            result = await db.blocked_chats.delete_many({})
            print(f"[CLEAN] Blocked Chats: {result.deleted_count} records deleted")
            total_deleted += result.deleted_count

    # 6. Clean assistant join history
    choice3 = input("[?] Clear assistant join history? (y/N): ").strip().lower()
    if choice3 == "y":
        if "assistant_chats" in collections:
            result = await db.assistant_chats.delete_many({})
            print(f"[CLEAN] Assistant Chats: {result.deleted_count} records deleted")
            total_deleted += result.deleted_count

    # 7. Show remaining collections sizes
    print("\n" + "=" * 50)
    print(f"  Total records deleted: {total_deleted}")
    print("=" * 50)
    print("\n[INFO] Remaining data in each collection:")
    for col in await db.list_collection_names():
        count = await db[col].count_documents({})
        print(f"  {col}: {count} records")

    print("\n[DONE] MongoDB cleanup complete!\n")
    client.close()


if __name__ == "__main__":
    asyncio.run(cleanup())
