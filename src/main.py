print("=" * 50)
print("PROGRAM STARTED")
print("=" * 50)

try:
    from dashboard import show_dashboard
    print("Dashboard module imported successfully")
    show_dashboard()
    print("Dashboard completed successfully")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()

print("=" * 50)
print("PROGRAM ENDED")
print("=" * 50)
input("Press Enter to exit...")