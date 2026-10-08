.PHONY: build test install uninstall

build:
	cargo build --locked --release --workspace --manifest-path native/Cargo.toml

test:
	python3 scripts/validate.py --hadalis-root "$(HADALIS_ROOT)"

install: build
	python3 scripts/install.py install

uninstall:
	python3 scripts/install.py uninstall
