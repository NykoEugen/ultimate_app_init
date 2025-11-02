from sqlalchemy import inspect, text
from app.db.base import engine

def main():
    with engine.begin() as conn:
        inspector = inspect(conn)
        cols = {c["name"] for c in inspector.get_columns("farm_player_stats")}
        if "starter_seed_charges" not in cols:
            conn.execute(
                text(
                    "ALTER TABLE farm_player_stats "
                    "ADD COLUMN starter_seed_charges INTEGER NOT NULL DEFAULT 1"
                )
            )
            print("Column starter_seed_charges added to farm_player_stats.")
        else:
            print("Column starter_seed_charges already present.")

if __name__ == "__main__":
    main()
