from database import Base, engine
import models

print("Creating tables...")
Base.metadata.create_all(bind=engine)
print("Done.")
