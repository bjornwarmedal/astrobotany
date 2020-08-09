#!/usr/bin/env python3
import argparse
from datetime import datetime, timedelta

from peewee import BlobField, BooleanField, DateTimeField, TextField
from playhouse import migrate

from astrobotany import items
from astrobotany.models import Certificate, Inbox, ItemSlot, User, gen_user_id, init_db


def add_setting_ansi_enabled(migrator):
    migrate.migrate(migrator.add_column("user", "ansi_enabled", BooleanField(default=False)))


def alter_user_id_type(migrator):
    migrate.migrate(
        migrator.alter_column_type("user", "user_id", TextField(unique=True, index=True))
    )


def add_item_paperclip(migrator):
    for user in User.select():
        ItemSlot.get_or_create(user=user, item_id=items.paperclip.item_id, defaults={"quantity": 1})


def add_item_fertilizer(migrator):
    for user in User.select():
        ItemSlot.get_or_create(
            user=user, item_id=items.fertilizer.item_id, defaults={"quantity": 5}
        )


def add_plant_fertilized_at(migrator):
    dt = datetime.now() - timedelta(days=4)
    migrate.migrate(migrator.add_column("plant", "fertilized_at", DateTimeField(default=dt)))


def send_welcome_message(migrator):
    for user in User.select():
        Inbox.send_welcome_message(user)


def add_user_password_field(migrator):
    migrate.migrate(migrator.add_column("user", "password", BlobField(null=True)))


def migrate_certificates(migrator):
    for user in User.select():
        Certificate.create(
            user=user,
            authorised=not user.user_id.endswith("="),
            fingerprint=user.user_id,
            cn=user.username,
        )
        user.user_id = gen_user_id()
        user.save()


MIGRATIONS = locals()


def main():
    parser = argparse.ArgumentParser(
        description="Apply a named migration to the astrobotany database"
    )
    parser.add_argument("migration")
    parser.add_argument("--db", default="/etc/astrobotany/astrobotany.sqlite")
    args = parser.parse_args()

    db = init_db(args.db)
    migrator = migrate.SqliteMigrator(db)

    print(f"Running migration {args.migration}...")
    MIGRATIONS[args.migration](migrator)
    print(f"Success!")


if __name__ == "__main__":
    main()
