def test_import():
    # This test simply tries to import the main module.
    # If this fails, there's a problem with the setup or dependencies.
    try:
        import lavacakes_pizza_fury.main
    except ImportError as e:
        assert False, f"Failed to import the main game module: {e}"