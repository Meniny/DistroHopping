#!/usr/bin/env python3
"""
distrohoping.py - A smart Linux distribution recommender.

Analyzes your hardware, current OS, and release model to suggest
the most suitable distribution - with a touch of cosmic mysticism.

No external dependencies required.
"""

import os
import platform
import random
import re
import sys
import time

# ---------------------------------------------------------------------------
# ANSI colour helpers
# ---------------------------------------------------------------------------

class C:
    """Terminal colour / style codes."""
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    BLACK   = "\033[30m"
    RED     = "\033[31m"
    GREEN   = "\033[32m"
    YELLOW  = "\033[33m"
    BLUE    = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN    = "\033[36m"
    WHITE   = "\033[37m"
    B_RED     = "\033[1;31m"
    B_GREEN   = "\033[1;32m"
    B_YELLOW  = "\033[1;33m"
    B_BLUE    = "\033[1;34m"
    B_MAGENTA = "\033[1;35m"
    B_CYAN    = "\033[1;36m"
    B_WHITE   = "\033[1;37m"
    B_BRED     = "\033[1;91m"
    B_BGREEN   = "\033[1;92m"
    B_BYELLOW  = "\033[1;93m"
    B_BBLUE    = "\033[1;94m"
    B_BMAGENTA = "\033[1;95m"
    B_BCYAN    = "\033[1;96m"
    B_BWHITE   = "\033[1;97m"


def colour(text, code):
    return f"{code}{text}{C.RESET}"


def bold(text):
    return f"{C.BOLD}{text}{C.RESET}"


def bold_colour(text, code):
    return f"{C.BOLD}{code}{text}{C.RESET}"


# ---------------------------------------------------------------------------
# Distro database
# ---------------------------------------------------------------------------
# weight categories:
#   "potato" - ancient / severely constrained hardware
#   "light"      - modest hardware (e.g. J4125 / Atom / Celeron class)
#   "standard"   - average / mid-range and above (covers everything from i5/Ryzen 5 up)
# current_os: which OS family the distro feels most natural coming from
# release: "stable", "rolling", "fixed"
# de: default / signature desktop environment

DISTROS = [
    # ---- Ultralight ----
    {
        "name": "Tiny Core Linux",
        "desc": "The smallest distro that still runs X. 16 MB of RAM? Done.",
        "color": C.B_BMAGENTA,
        "bold": True,
        "weight": "potato",
        "current_os": ["linux"],
        "release": "fixed",
        "de": "flwm",
    },
    {
        "name": "Puppy Linux",
        "desc": "Runs entirely in RAM. Blazing fast even on a potato.",
        "color": C.B_BYELLOW,
        "bold": True,
        "weight": "potato",
        "current_os": ["linux", "windows"],
        "release": "fixed",
        "de": "jwm",
    },
    {
        "name": "antiX",
        "desc": "Debian-based, systemd-free, runs on Pentium III. Seriously.",
        "color": C.B_BGREEN,
        "bold": False,
        "weight": "potato",
        "current_os": ["linux", "windows"],
        "release": "stable",
        "de": "icewm",
    },
    {
        "name": "Slitaz",
        "desc": "A complete Linux distro in ~50 MB. Yes, really.",
        "color": C.B_BCYAN,
        "bold": False,
        "weight": "potato",
        "current_os": ["linux"],
        "release": "fixed",
        "de": "openbox",
    },
    {
        "name": "Damn Small Linux",
        "desc": "The name says it all. Revived and ready for old hardware.",
        "color": C.B_BWHITE,
        "bold": False,
        "weight": "potato",
        "current_os": ["linux", "windows"],
        "release": "fixed",
        "de": "jwm",
    },
    # ---- Light ----
    {
        "name": "Lubuntu",
        "desc": "Ubuntu with LXQt. Familiar repos, light on resources.",
        "color": C.B_BBLUE,
        "bold": False,
        "weight": "light",
        "current_os": ["linux", "windows"],
        "release": "fixed",
        "de": "lxqt",
    },
    {
        "name": "Xubuntu",
        "desc": "Ubuntu + XFCE. A proven, lightweight workhorse.",
        "color": C.B_BBLUE,
        "bold": False,
        "weight": "light",
        "current_os": ["linux", "windows"],
        "release": "fixed",
        "de": "xfce",
    },
    {
        "name": "Linux Mint XFCE",
        "desc": "Mint's polish in a lightweight XFCE package.",
        "color": C.B_GREEN,
        "bold": False,
        "weight": "light",
        "current_os": ["linux", "windows"],
        "release": "stable",
        "de": "xfce",
    },
    {
        "name": "Void Linux XFCE",
        "desc": "Runit init, xbps, rolling but stable. The cool kid's lightweight.",
        "color": C.B_GREEN,
        "bold": True,
        "weight": "light",
        "current_os": ["linux"],
        "release": "rolling",
        "de": "xfce",
    },
    {
        "name": "Bodhi Linux",
        "desc": "Ubuntu-based with the gorgeous Moksha desktop.",
        "color": C.B_BCYAN,
        "bold": False,
        "weight": "light",
        "current_os": ["linux", "windows"],
        "release": "fixed",
        "de": "moksha",
    },
    {
        "name": "Q4OS",
        "desc": "Debian-based with a Windows-like Trinity desktop. Great transition distro.",
        "color": C.B_BGREEN,
        "bold": False,
        "weight": "light",
        "current_os": ["windows"],
        "release": "stable",
        "de": "trinity",
    },
    {
        "name": "Peppermint OS",
        "desc": "Cloud-focused, lightweight, Debian-based. Simple and fast.",
        "color": C.B_BBLUE,
        "bold": False,
        "weight": "light",
        "current_os": ["linux", "windows"],
        "release": "fixed",
        "de": "xfce",
    },
    {
        "name": "Alpine Linux",
        "desc": "Security-focused, musl + busybox. Tiny footprint, big brain energy.",
        "color": C.B_BBLUE,
        "bold": False,
        "weight": "light",
        "current_os": ["linux"],
        "release": "rolling",
        "de": "none",
    },
    # ---- Medium ----
    {
        "name": "Linux Mint",
        "desc": "The gold standard for a ready-to-use desktop Linux experience.",
        "color": C.B_GREEN,
        "bold": False,
        "weight": "standard",
        "current_os": ["linux", "windows"],
        "release": "stable",
        "de": "cinnamon",
    },
    {
        "name": "Ubuntu",
        "desc": "The most well-known Linux. Snaps included whether you like it or not.",
        "color": C.B_BRED,
        "bold": False,
        "weight": "standard",
        "current_os": ["linux", "windows"],
        "release": "fixed",
        "de": "gnome",
    },
    {
        "name": "Fedora Workstation",
        "desc": "Cutting-edge GNOME, Linus Torvalds uses it. What more do you need?",
        "color": C.B_BBLUE,
        "bold": True,
        "weight": "standard",
        "current_os": ["linux", "windows", "macos"],
        "release": "fixed",
        "de": "gnome",
    },
    {
        "name": "Pop!_OS",
        "desc": "Ubuntu-based with tiling wm goodness. Great for NVIDIA out of the box.",
        "color": C.B_BCYAN,
        "bold": True,
        "weight": "standard",
        "current_os": ["linux", "windows"],
        "release": "fixed",
        "de": "cosmic",
    },
    {
        "name": "Zorin OS",
        "desc": "The most Windows/macOS-like Linux. Perfect for newcomers.",
        "color": C.B_BMAGENTA,
        "bold": True,
        "weight": "standard",
        "current_os": ["windows", "macos"],
        "release": "fixed",
        "de": "gnome",
    },
    {
        "name": "elementary OS",
        "desc": "macOS aesthetics baked in. Pantheon desktop is gorgeous.",
        "color": C.B_BBLUE,
        "bold": True,
        "weight": "standard",
        "current_os": ["macos"],
        "release": "fixed",
        "de": "pantheon",
    },
    {
        "name": "Debian",
        "desc": "The universal operating system. Rock-solid stable. The distro behind Mint, Ubuntu, Pop and many more.",
        "color": C.B_BRED,
        "bold": False,
        "weight": "standard",
        "current_os": ["linux"],
        "release": "stable",
        "de": "gnome",
    },
    {
        "name": "openSUSE",
        "desc": "Versatile, stable, with the little green chameleon. YaST is unmatched.",
        "color": C.B_BGREEN,
        "bold": True,
        "weight": "standard",
        "current_os": ["linux", "windows"],
        "release": "stable",
        "de": "gnome",
    },
    {
        "name": "Nobara Project",
        "desc": "Fedora-based, gaming-optimized by GloriousEggroll. Proton + Wine preconfigured.",
        "color": C.B_BMAGENTA,
        "bold": True,
        "weight": "standard",
        "current_os": ["linux", "windows"],
        "release": "fixed",
        "de": "gnome",
    },
    {
        "name": "KaOS",
        "desc": "Independent KDE-focused rolling distro. Calamares installer, Qt-centric.",
        "color": C.B_BBLUE,
        "bold": False,
        "weight": "standard",
        "current_os": ["linux"],
        "release": "rolling",
        "de": "kde",
    },
    # ---- Heavy ----
    {
        "name": "Arch Linux",
        "desc": "I use Arch btw. Rolling, minimal, DIY. The AUR is legendary.",
        "color": C.B_BCYAN,
        "bold": True,
        "weight": "standard",
        "current_os": ["linux"],
        "release": "rolling",
        "de": "none",
    },
    {
        "name": "EndeavourOS",
        "desc": "Arch without the pain. Friendly installer, close-to-pure Arch.",
        "color": C.B_BMAGENTA,
        "bold": True,
        "weight": "standard",
        "current_os": ["linux"],
        "release": "rolling",
        "de": "xfce",
    },
    {
        "name": "Garuda Linux",
        "desc": "Arch-based, BTRFS + snapshots, gaming-optimized. Arch on steroids.",
        "color": C.B_BCYAN,
        "bold": True,
        "weight": "standard",
        "current_os": ["linux"],
        "release": "rolling",
        "de": "kde",
    },
    {
        "name": "Manjaro",
        "desc": "User-friendly Arch with its own repos. Good for Arch-curious beginners.",
        "color": C.B_BGREEN,
        "bold": True,
        "weight": "standard",
        "current_os": ["linux", "windows"],
        "release": "rolling",
        "de": "kde",
    },
    {
        "name": "NixOS",
        "desc": "Declarative, reproducible. Manage your entire system in code. Steep curve, infinite power.",
        "color": C.B_BMAGENTA,
        "bold": True,
        "weight": "standard",
        "current_os": ["linux"],
        "release": "rolling",
        "de": "gnome",
    },
    {
        "name": "Gentoo",
        "desc": "Compile everything from source. USE flags are your paintbrush. Enjoy the compile time!",
        "color": C.B_BMAGENTA,
        "bold": True,
        "weight": "standard",
        "current_os": ["linux"],
        "release": "rolling",
        "de": "none",
    },
    {
        "name": "Linux From Scratch",
        "desc": "You chose death... just kidding. Build Linux from zero. Ultimate learning experience.",
        "color": C.B_BWHITE,
        "bold": False,
        "weight": "standard",
        "current_os": ["linux"],
        "release": "fixed",
        "de": "none",
    },
    {
        "name": "Fedora KDE",
        "desc": "Fedora's cutting-edge packages with the full KDE Plasma experience.",
        "color": C.B_BBLUE,
        "bold": False,
        "weight": "standard",
        "current_os": ["linux", "windows", "macos"],
        "release": "fixed",
        "de": "kde",
    },
    {
        "name": "MX Linux",
        "desc": "Debian-based, XFCE by default. Consistently tops DistroWatch for a reason.",
        "color": C.B_BCYAN,
        "bold": False,
        "weight": "standard",
        "current_os": ["linux", "windows"],
        "release": "stable",
        "de": "xfce",
    },
    # ---- BSD / Special ----
    {
        "name": "FreeBSD",
        "desc": "Performance and networking champ. ZFS + jails are enterprise-grade.",
        "color": C.B_BRED,
        "bold": False,
        "weight": "standard",
        "current_os": ["linux", "bsd"],
        "release": "stable",
        "de": "none",
    },
    {
        "name": "OpenBSD",
        "desc": "Security-obsessed, code correctness first. Only two remote holes in a heck of a long time.",
        "color": C.B_BYELLOW,
        "bold": True,
        "weight": "standard",
        "current_os": ["linux", "bsd"],
        "release": "stable",
        "de": "none",
    },
    {
        "name": "GhostBSD",
        "desc": "FreeBSD with MATE desktop, ready to use. The friendliest BSD.",
        "color": C.B_BYELLOW,
        "bold": False,
        "weight": "standard",
        "current_os": ["linux", "bsd"],
        "release": "stable",
        "de": "mate",
    },
    {
        "name": "Kali Linux",
        "desc": "The hacker's Debian. Loaded with pentesting tools. Don't be a script kiddie.",
        "color": C.B_BBLUE,
        "bold": True,
        "weight": "standard",
        "current_os": ["linux", "windows"],
        "release": "rolling",
        "de": "xfce",
    },
    {
        "name": "Tails OS",
        "desc": "Tinfoil hat activated. Tor + I2P built-in. Maximum privacy, live USB only.",
        "color": C.BLACK,
        "bold": True,
        "weight": "light",
        "current_os": ["linux", "windows", "macos"],
        "release": "fixed",
        "de": "gnome",
    },
    {
        "name": "Qubes OS",
        "desc": "Security by isolation. Every app in its own VM. The most paranoid desktop.",
        "color": C.B_BWHITE,
        "bold": False,
        "weight": "standard",
        "current_os": ["linux", "windows"],
        "release": "fixed",
        "de": "xfce",
    },
    {
        "name": "Vanilla OS",
        "desc": "Immutable, Apx lets you install packages from any distro. The future of Linux?",
        "color": C.B_BYELLOW,
        "bold": False,
        "weight": "standard",
        "current_os": ["linux"],
        "release": "fixed",
        "de": "gnome",
    },
    {
        "name": "Bedrock Linux",
        "desc": "Run packages from incompatible distros side by side. Franken-distro done right.",
        "color": C.BLACK,
        "bold": True,
        "weight": "standard",
        "current_os": ["linux"],
        "release": "rolling",
        "de": "none",
    },
    {
        "name": "TrueNAS SCALE",
        "desc": "Debian-based NAS powerhouse. ZFS, containers, VMs. Your data fortress.",
        "color": C.B_BBLUE,
        "bold": False,
        "weight": "standard",
        "current_os": ["linux", "bsd"],
        "release": "stable",
        "de": "none",
    },
    # ---- More from DistroWatch hit rankings ----
    # Ultralight additions
    {
        "name": "SparkyLinux",
        "desc": "Debian-based, fast and lightweight. XFCE or LXQt editions shine on old hardware.",
        "color": C.B_BGREEN,
        "bold": False,
        "weight": "potato",
        "current_os": ["linux", "windows"],
        "release": "stable",
        "de": "xfce",
    },
    {
        "name": "Mageia",
        "desc": "Mandriva successor, community-driven. A solid all-rounder with great tools.",
        "color": C.B_BYELLOW,
        "bold": False,
        "weight": "light",
        "current_os": ["linux", "windows"],
        "release": "fixed",
        "de": "gnome",
    },
    # Light additions
    {
        "name": "Linux Lite",
        "desc": "Windows-friendly XFCE distro. Designed for simplicity and speed on older machines.",
        "color": C.B_BYELLOW,
        "bold": False,
        "weight": "light",
        "current_os": ["windows"],
        "release": "fixed",
        "de": "xfce",
    },
    {
        "name": "Zorin OS Lite",
        "desc": "Zorin's Windows-like polish in a lightweight XFCE package.",
        "color": C.B_BMAGENTA,
        "bold": False,
        "weight": "light",
        "current_os": ["windows"],
        "release": "fixed",
        "de": "xfce",
    },
    {
        "name": "Devuan",
        "desc": "Debian without systemd. For those who value init freedom.",
        "color": C.B_BRED,
        "bold": False,
        "weight": "light",
        "current_os": ["linux"],
        "release": "stable",
        "de": "xfce",
    },
    {
        "name": "Emmabuntus",
        "desc": "Xubuntu-based, designed for humanitarian organizations. Lightweight and ready to go.",
        "color": C.B_BGREEN,
        "bold": False,
        "weight": "light",
        "current_os": ["linux", "windows"],
        "release": "fixed",
        "de": "xfce",
    },
    {
        "name": "Trisquel",
        "desc": "100% free-software distro. FSF-approved, GNU/Linux-libre kernel.",
        "color": C.B_BMAGENTA,
        "bold": False,
        "weight": "light",
        "current_os": ["linux"],
        "release": "fixed",
        "de": "mate",
    },
    {
        "name": "Feren OS",
        "desc": "Elegant, Windows-like distro with KDE. Polished out of the box.",
        "color": C.B_BBLUE,
        "bold": False,
        "weight": "light",
        "current_os": ["windows"],
        "release": "fixed",
        "de": "kde",
    },
    # Medium additions
    {
        "name": "Solus",
        "desc": "Independent, built from scratch with Budgie desktop. Smooth and curated.",
        "color": C.B_BCYAN,
        "bold": True,
        "weight": "standard",
        "current_os": ["linux", "windows"],
        "release": "rolling",
        "de": "budgie",
    },
    {
        "name": "Deepin",
        "desc": "Stunning DDE desktop. Beautiful, but a bit heavy. Chinese origins, global appeal.",
        "color": C.B_BBLUE,
        "bold": True,
        "weight": "standard",
        "current_os": ["linux", "windows", "macos"],
        "release": "fixed",
        "de": "dde",
    },
    {
        "name": "Ultramarine Linux",
        "desc": "Fedora-based with extra codecs and tweaks. Fedora without the post-setup hassle.",
        "color": C.B_BCYAN,
        "bold": False,
        "weight": "standard",
        "current_os": ["linux", "windows"],
        "release": "fixed",
        "de": "gnome",
    },
    {
        "name": "Asahi Linux",
        "desc": "Linux on Apple Silicon. Bringing the penguin to M-series Macs.",
        "color": C.B_BYELLOW,
        "bold": True,
        "weight": "standard",
        "current_os": ["macos"],
        "release": "fixed",
        "de": "gnome",
    },
    {
        "name": "Regata OS",
        "desc": "openSUSE-based, gaming-focused from Brazil. Game access built in.",
        "color": C.B_BRED,
        "bold": False,
        "weight": "standard",
        "current_os": ["linux", "windows"],
        "release": "fixed",
        "de": "kde",
    },
    {
        "name": "CentOS Stream",
        "desc": "RHEL upstream. The middle ground between Fedora's bleeding edge and RHEL's stability.",
        "color": C.B_BGREEN,
        "bold": False,
        "weight": "standard",
        "current_os": ["linux"],
        "release": "rolling",
        "de": "gnome",
    },
    {
        "name": "AlmaLinux",
        "desc": "RHEL binary-compatible, community-governed. The enterprise choice after CentOS shifted.",
        "color": C.B_BYELLOW,
        "bold": False,
        "weight": "standard",
        "current_os": ["linux"],
        "release": "stable",
        "de": "gnome",
    },
    {
        "name": "Rocky Linux",
        "desc": "RHEL clone by CentOS co-founder. Enterprise-grade, free and open.",
        "color": C.B_BGREEN,
        "bold": False,
        "weight": "standard",
        "current_os": ["linux"],
        "release": "stable",
        "de": "gnome",
    },
    {
        "name": "Slackware",
        "desc": "The oldest surviving distro. KISS principle incarnate. Not for the faint of heart.",
        "color": C.B_BMAGENTA,
        "bold": True,
        "weight": "standard",
        "current_os": ["linux"],
        "release": "stable",
        "de": "none",
    },
    # Heavy additions
    {
        "name": "Clear Linux",
        "desc": "Intel's performance-optimized distro. Benchmarks don't lie.",
        "color": C.B_BBLUE,
        "bold": True,
        "weight": "standard",
        "current_os": ["linux"],
        "release": "rolling",
        "de": "gnome",
    },
    {
        "name": "OpenMandriva Lx",
        "desc": "Mandriva's spiritual successor. KDE-focused with unique tools.",
        "color": C.B_BYELLOW,
        "bold": False,
        "weight": "standard",
        "current_os": ["linux", "windows"],
        "release": "rolling",
        "de": "kde",
    },
    {
        "name": "Artix Linux",
        "desc": "Arch without systemd. Choose your init: runit, s6, openrc. Freedom of choice.",
        "color": C.B_BCYAN,
        "bold": True,
        "weight": "standard",
        "current_os": ["linux"],
        "release": "rolling",
        "de": "none",
    },
    {
        "name": "CachyOS",
        "desc": "Arch-based with optimized kernels and x86-64-v3 builds. Speed demon.",
        "color": C.B_BMAGENTA,
        "bold": True,
        "weight": "standard",
        "current_os": ["linux"],
        "release": "rolling",
        "de": "kde",
    },
    {
        "name": "SteamOS",
        "desc": "Valve's Arch-based gaming OS. Deck-proven, desktop-ready. Gaming's future on Linux.",
        "color": C.B_BBLUE,
        "bold": True,
        "weight": "standard",
        "current_os": ["linux", "windows"],
        "release": "rolling",
        "de": "kde",
    },
    {
        "name": "NetBSD",
        "desc": "Runs on everything from a toaster to a server. 'Of course it runs NetBSD.'",
        "color": C.B_BRED,
        "bold": False,
        "weight": "standard",
        "current_os": ["linux", "bsd"],
        "release": "stable",
        "de": "none",
    },
    {
        "name": "DragonFly BSD",
        "desc": "Forked from FreeBSD, HAMMER2 filesystem, innovative design. BSD with a twist.",
        "color": C.B_BRED,
        "bold": False,
        "weight": "standard",
        "current_os": ["linux", "bsd"],
        "release": "stable",
        "de": "none",
    },
    {
        "name": "Haiku",
        "desc": "BeOS reborn. Fast, focused, and delightfully different. Not Linux, but awesome.",
        "color": C.B_BRED,
        "bold": True,
        "weight": "light",
        "current_os": ["linux", "windows", "macos"],
        "release": "rolling",
        "de": "haiku",
    },
    # More niche / special
    {
        "name": "Parrot OS",
        "desc": "Debian-based security distro. Kali alternative with MATE desktop and privacy tools.",
        "color": C.B_BCYAN,
        "bold": True,
        "weight": "standard",
        "current_os": ["linux", "windows"],
        "release": "rolling",
        "de": "mate",
    },
    {
        "name": "NethServer",
        "desc": "CentOS-based server distro. Firewall, mail, file server all in one.",
        "color": C.B_BGREEN,
        "bold": False,
        "weight": "standard",
        "current_os": ["linux"],
        "release": "stable",
        "de": "none",
    },
]


# ---------------------------------------------------------------------------
# CPU database
# ---------------------------------------------------------------------------
# TDP / performance tier mapping. Covers the most common desktop / laptop CPUs
# from the last ~15 years plus server / special chips.

CPU_TIERS = {
    # fmt: off
    # ---- Ultralight tier (ancient / extremely low-power) ----
    "potato": [
        # Intel Atom
        "atom n270", "atom n280", "atom n450", "atom n455", "atom n550",
        "atom d525", "atom z2760", "atom z3735f", "atom x5-z8350",
        "atom x7-z8700", "atom e3825", "atom e3845",
        # Intel Celeron (older / low-end)
        "celeron n2840", "celeron n2815", "celeron n2940", "celeron n3050",
        "celeron n3060", "celeron n3350", "celeron n3450", "celeron n4000",
        "celeron n4020", "celeron n4100", "celeron n4120", "celeron n4500",
        "celeron j1800", "celeron j1900", "celeron 847", "celeron 1007u",
        "celeron 1037u", "celeron g1610", "celeron g1820", "celeron g1840",
        "celeron g3900", "celeron g3930", "celeron g4900", "celeron g4920",
        "celeron g5900", "celeron g5905", "celeron g6900",
        # Intel Pentium (older)
        "pentium n3700", "pentium n4200", "pentium n5000",
        "pentium e2200", "pentium g620", "pentium g2020", "pentium g2030",
        "pentium g3258", "pentium g4400", "pentium g4560", "pentium g5400",
        "pentium gold g6400", "pentium silver j5005",
        # AMD low-end
        "e-350", "e-450", "e1-2500", "e2-1800", "e2-6110", "e2-9000",
        "a4-3300", "a4-5000", "a6-5200", "a6-7310", "a6-9200", "a6-9225",
        # VIA / others
        "via c7", "via eden", "geode", "transmeta crusoe",
        # Very old
        "pentium iii", "pentium 4", "pentium m", "pentium d",
        "athlon xp", "athlon 64", "sempron", "durron",
        "core 2 duo", "core 2 quad", "celeron m", "pentium dual-core",
        # ARM low-end
        "armv7", "cortex-a7", "cortex-a53", "cortex-a55",
        "bcm2835", "bcm2837",  # Raspberry Pi 1/3
        "allwinner a64", "rockchip rk3288", "rockchip rk3399",
    ],
    # ---- Light tier (modest, J4125-class) ----
    "light": [
        # Intel low-mid
        "celeron n5105", "celeron n6000", "celeron 3865u", "celeron 4205u",
        "celeron 5205u", "celeron 5305u", "celeron 6305", "celeron 7305",
        "pentium gold g6405", "pentium silver n6000",
        # Apollo / Gemini Lake
        "celeron j4105", "celeron j4115", "celeron j4125",
        "celeron j5005", "celeron j5040",
        "pentium silver n5000", "pentium silver n5030",
        # Intel U-series older
        "i3-2350m", "i3-3110m", "i3-4005u", "i3-4010u", "i3-4030u",
        "i3-5005u", "i3-6006u", "i3-7020u", "i3-7100u",
        "i3-8130u", "i3-1005g1", "i3-10110u", "i3-1115g4",
        # AMD A-series
        "a8-5500", "a8-7600", "a10-5800k", "a10-7850k",
        "a10-9700", "a12-9800", "ryon 3 2200u", "ryon 3 3200u",
        "ryon 3 3250u", "ryon 3 5300u",
        # Older desktop
        "i5-2500", "i5-3470", "i5-4570", "i5-6500",
        "fx-4300", "fx-6300", "fx-8300", "fx-8350",
        # ARM SBC
        "bcm2711", "bcm2712",  # Raspberry Pi 4/5
    ],
    # ---- Standard tier (mid-range and above) ----
    "standard": [
        # Intel 8th-10th gen mainstream
        "i3-12100", "i3-12100f", "i3-13100",
        "i5-8250u", "i5-8265u", "i5-8300h", "i5-8400", "i5-8500", "i5-8600k",
        "i5-9300h", "i5-9400", "i5-9400f", "i5-9600k",
        "i5-10210u", "i5-1035g1", "i5-10400", "i5-10400f", "i5-10600k",
        "i5-1135g7", "i5-11400", "i5-11400f", "i5-11600k",
        "i5-1235u", "i5-12400", "i5-12400f", "i5-12500h", "i5-12600k",
        "i5-13400", "i5-13400f", "i5-13500h", "i5-13600k",
        "i7-8550u", "i7-8565u", "i7-8700", "i7-8700k",
        "i7-9700", "i7-9700k", "i7-10510u", "i7-10700", "i7-10700k",
        "i7-1165g7", "i7-11700", "i7-11700k",
        "i7-1255u", "i7-1260p", "i7-12700", "i7-12700k",
        "i7-1355u", "i7-1360p", "i7-13700", "i7-13700k",
        # Intel high-end desktop
        "i7-13700kf", "i7-14700k", "i7-14700kf",
        "i9-9900k", "i9-10900k", "i9-11900k", "i9-11900h",
        "i9-12900k", "i9-12900kf", "i9-13900k", "i9-13900kf",
        "i9-14900k", "i9-14900kf",
        "i9-10980xe", "i9-10940x",
        # AMD Ryzen mainstream
        "ryzen 3 4100", "ryzen 3 4300g", "ryzen 5 1500x", "ryzen 5 1600",
        "ryzen 5 2600", "ryzen 5 3400g", "ryzen 5 3500x", "ryzen 5 3600",
        "ryzen 5 4500u", "ryzen 5 4600g", "ryzen 5 4600h", "ryzen 5 4600u",
        "ryzen 5 5500", "ryzen 5 5500u", "ryzen 5 5600", "ryzen 5 5600g",
        "ryzen 5 5600h", "ryzen 5 5600x", "ryzen 5 5625u",
        "ryzen 5 6600h", "ryzen 5 6600u",
        "ryzen 5 7520u", "ryzen 5 7535hs", "ryzen 5 7600", "ryzen 5 7600x",
        "ryzen 7 1700", "ryzen 7 2700", "ryzen 7 3700x",
        "ryzen 7 4700u", "ryzen 7 4800h", "ryzen 7 4800u",
        "ryzen 7 5700g", "ryzen 7 5700u", "ryzen 7 5800h", "ryzen 7 5800x",
        "ryzen 7 5800x3d", "ryzen 7 6800h", "ryzen 7 6800u",
        "ryzen 7 7700", "ryzen 7 7700x", "ryzen 7 7840hs", "ryzen 7 7840u",
        "ryzen 9 3900x", "ryzen 9 5900x", "ryzen 9 5900hx",
        "ryzen 9 6900hx", "ryzen 9 7900x", "ryzen 9 7945hx",
        "ryzen 9 7940hs", "ryzen 9 7950x",
        "ryzen 9 9950x", "ryzen 9 9900x", "ryzen 7 9700x", "ryzen 5 9600x",
        "ryzen 9 3950x", "ryzen 9 7950x3d",
        "ryzen 9 7900x3d", "ryzen 7 7800x3d",
        # Apple
        "apple m2", "apple m2 pro", "apple m2 max",
        "apple m3", "apple m3 pro", "apple m3 max",
        "apple m4", "apple m4 pro", "apple m4 max",
        "apple m1 ultra", "apple m2 ultra",
        # Intel Xeon
        "xeon",
        # AMD Threadripper / high-end
        "threadripper",
        # Nvidia Jetson (edge)
        "tegra x1", "jetson agx",
        # High-end ARM server
        "ampere altra", "cortex-x1", "cortex-x2", "cortex-x3", "cortex-x4",
        # Generic high-end catch
        "epyc", "xeon gold", "xeon platinum",
    ],
    # fmt: on
}


def cpu_tier(cpu_string):
    """Return 'potato', 'light', or 'standard' based on CPU string.

    First tries exact substring match against the database, then falls back
    to heuristic pattern matching for unknown / future CPUs.
    """
    if not cpu_string:
        return "light"
    cpu_lower = cpu_string.lower().strip()

    # 1. Exact substring match
    for tier_name, cpus in CPU_TIERS.items():
        for pattern in cpus:
            if pattern in cpu_lower:
                return tier_name

    # 2. Heuristic pattern matching for unknown / future CPUs
    # Apple Silicon: all M-series are standard
    if re.search(r'apple\s*m\d', cpu_lower) or 'apple silicon' in cpu_lower:
        return "standard"

    # Intel Core i3/i5/i7/i9/Ultra — extract generation digit
    core_match = re.search(r'(?:core.*?)(?:i[3579]|ultra\s*\d)\s*[-]?(\d{4,5})', cpu_lower)
    if core_match:
        gen = int(core_match.group(1)[0])  # first digit = generation
        if gen <= 3:
            return "light"     # 1st-3rd gen: aging
        return "standard"      # 4th gen+: still capable

    # Intel "Core Ultra" without model number match
    if 'core ultra' in cpu_lower:
        return "standard"

    # Intel Celeron / Pentium — usually potato or light
    if re.search(r'celeron|pentium', cpu_lower):
        # Newer Celeron (N-series like N100/N200) → light
        if re.search(r'\bn[1-9]\d{2}\b', cpu_lower):
            return "light"
        return "potato"

    # AMD Ryzen 3/5/7/9 — all are standard or better
    if re.search(r'ryzen\s*(?:ai\s+)?[3579]', cpu_lower):
        return "standard"

    # AMD A-series / Athlon — light to potato
    if re.search(r'(?:a[4689]|a10|a12|athlon)\s', cpu_lower):
        return "potato"

    # Snapdragon / ARM laptop chips — light
    if 'snapdragon' in cpu_lower or 'oryon' in cpu_lower:
        return "light"

    # ARM Cortex — A7x/A5x = potato/lite, X-series = standard
    if 'cortex-x' in cpu_lower:
        return "standard"
    if 'cortex-a' in cpu_lower:
        return "potato"

    # Server / workstation (Xeon, EPYC, Threadripper)
    if re.search(r'(xeon|epyc|threadripper)', cpu_lower):
        return "standard"

    # VIA / Geode / old stuff
    if re.search(r'(via|geode|transmeta)', cpu_lower):
        return "potato"

    # 3. Ultimate fallback
    return "light"


# ---------------------------------------------------------------------------
# System detection
# ---------------------------------------------------------------------------

def detect_current_os():
    """Return 'linux', 'windows', 'macos', 'bsd', or 'unknown'."""
    system = platform.system().lower()
    if "linux" in system:
        return "linux"
    if "windows" in system:
        return "windows"
    if "darwin" in system:
        return "macos"
    if "freebsd" in system or "openbsd" in system or "netbsd" in system:
        return "bsd"
    # Fallback: check for WSL
    try:
        with open("/proc/version", encoding="utf-8", errors="ignore") as f:
            ver = f.read().lower()
            if "microsoft" in ver:
                return "windows"
    except OSError:
        pass
    return "unknown"


def detect_distro_family():
    """Detect current Linux distro family category."""
    try:
        import subprocess
        result = subprocess.run(
            ["cat", "/etc/os-release"], capture_output=True, text=True, timeout=3
        )
        if result.returncode == 0:
            content = result.stdout.lower()
            if "arch" in content or "endeavouros" in content or "manjaro" in content or "garuda" in content:
                return "arch"
            if "debian" in content or "ubuntu" in content or "mint" in content or "pop" in content or "zorin" in content or "elementary" in content:
                return "debian"
            if "fedora" in content or "nobara" in content:
                return "fedora"
            if "void" in content:
                return "void"
            if "gentoo" in content:
                return "gentoo"
            if "alpine" in content:
                return "alpine"
            if "nixos" in content:
                return "nixos"
            if "opensuse" in content or "suse" in content:
                return "suse"
    except Exception:
        pass
    return "unknown"


def detect_distro_name():
    """Return the current Linux distro display name (e.g. 'Debian', 'Arch Linux')."""
    try:
        with open("/etc/os-release", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if line.startswith("PRETTY_NAME="):
                    return line.split("=", 1)[1].strip().strip('"')
    except OSError:
        pass
    return "Linux"


def detect_is_rolling():
    """Guess whether the current system is rolling-release."""
    system = detect_current_os()
    if system == "linux":
        family = detect_distro_family()
        return family in ("arch", "void", "alpine", "gentoo", "nixos")
    return False


def detect_ram_gb():
    """Return total RAM in GB (int)."""
    try:
        if platform.system() == "Linux":
            with open("/proc/meminfo", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("MemTotal:"):
                        kb = int(line.split()[1])
                        return kb // (1024 * 1024)
        elif platform.system() == "Darwin":
            import subprocess
            out = subprocess.check_output(["sysctl", "-n", "hw.memsize"], text=True)
            return int(out.strip()) // (1024 ** 3)
        elif platform.system() == "Windows":
            import subprocess
            out = subprocess.check_output(
                ["wmic", "ComputerSystem", "get", "TotalPhysicalMemory"], text=True
            )
            bytes_val = int(out.strip().split("\n")[1].strip())
            return bytes_val // (1024 ** 3)
    except Exception:
        pass
    return 0


def detect_cpu():
    """Return CPU model string. Reads /proc/cpuinfo on Linux for accuracy."""
    # Try /proc/cpuinfo first (works on real Linux and VMs with host passthrough)
    try:
        with open("/proc/cpuinfo", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if line.startswith("model name") or line.startswith("Hardware"):
                    # "model name\t: Intel(R) Xeon(R) Gold 6248R CPU @ 3.00GHz"
                    return line.split(":", 1)[1].strip()
    except OSError:
        pass
    # Fallback for macOS / others
    try:
        import subprocess
        if platform.system() == "Darwin":
            return subprocess.check_output(
                ["sysctl", "-n", "machdep.cpu.brand_string"], text=True
            ).strip()
    except Exception:
        pass
    return platform.processor() or ""


def effective_weight(cpu_tier, ram_gb):
    """Adjust CPU tier by RAM. Low RAM can downgrade the effective tier."""
    if ram_gb <= 2:
        return "potato"
    if ram_gb <= 4:
        if cpu_tier == "standard":
            return "light"
        return min_weight(cpu_tier, "light")
    return cpu_tier


def min_weight(a, b):
    order = ["potato", "light", "standard"]
    return a if order.index(a) <= order.index(b) else b


# ---------------------------------------------------------------------------
# Recommendation engine
# ---------------------------------------------------------------------------

# Compatibility groups for release-model & distro-family matching
ROLLING_GROUP = {"arch", "void", "gentoo", "nixos", "alpine", "bedrock"}
STABLE_GROUP  = {"debian", "fedora", "suse"}

DE_PREFERENCE = {
    "windows": "cinnamon",  # Windows users -> familiar taskbar DEs
    "macos": "gnome",       # macOS users -> GNOME / polished DEs
}


def recommend(cpu, ram_gb, current_os, is_rolling, distro_family):
    """Return (candidates: list[dict], final: dict)."""

    tier = cpu_tier(cpu)
    eff = effective_weight(tier, ram_gb)

    # Build weight filter: allow the effective tier +/- one level
    weight_order = ["potato", "light", "standard"]
    eff_idx = weight_order.index(eff)
    allowed_weights = set()
    for delta in (-1, 0, 1):
        idx = eff_idx + delta
        if 0 <= idx < len(weight_order):
            allowed_weights.add(weight_order[idx])

    # Score each distro
    scored = []
    for d in DISTROS:
        score = 0

        # 1. Weight match (primary filter)
        if d["weight"] not in allowed_weights:
            continue  # hard filter
        if d["weight"] == eff:
            score += 10  # best match
        elif abs(weight_order.index(d["weight"]) - eff_idx) == 1:
            score += 5

        # 2. Current OS compatibility
        if current_os in d.get("current_os", []):
            score += 8
        elif current_os == "macos" and d["de"] in ("gnome", "pantheon"):
            score += 5  # macOS users like polished DEs
        elif current_os == "windows" and d["de"] in ("cinnamon", "kde", "gnome"):
            score += 4  # familiar layouts

        # 3. Release model continuity
        if is_rolling and d["release"] == "rolling":
            score += 7
        elif not is_rolling and d["release"] in ("stable", "fixed"):
            score += 3

        # 4. Distro family affinity
        if distro_family in ROLLING_GROUP and d["release"] == "rolling":
            score += 6
        if distro_family in STABLE_GROUP and d["release"] in ("stable", "fixed"):
            score += 4
        # Cross-family: arch/void/gentoo/lfs <-> each other
        if distro_family in ("arch", "void", "gentoo") and d.get("name", "").lower() in (
            "arch linux", "void linux", "gentoo", "linux from scratch",
            "endeavouros", "garuda linux",
        ):
            score += 8
        if distro_family == "debian" and d.get("name", "").lower() in (
            "debian", "linux mint", "ubuntu", "pop!_os", "zorin os",
            "elementary os", "mx linux", "vanilla os", "q4os", "bodhi linux",
            "peppermint os", "tails os", "kali linux",
        ):
            score += 5

        scored.append((score, d))

    # Fallback: if nothing matched at all (shouldn't happen, but safety net)
    if not scored:
        scored = [(random.randint(0, 10), d) for d in DISTROS]

    # Sort by score descending
    scored.sort(key=lambda x: x[0], reverse=True)

    # Take top candidates
    max_score = scored[0][0]
    # Get all with score within 5 of max (to have a pool)
    pool = [d for s, d in scored if s >= max_score - 5]

    # Pick top 3 for the "thinking" animation
    random.shuffle(pool)
    candidates = pool[:3]

    # Final pick: weighted random favouring highest score
    weights = []
    for d in candidates:
        s = next(sc for sc, dd in scored if dd is d)
        weights.append(s + 1)
    final = random.choices(candidates, weights=weights, k=1)[0]

    return candidates, final


# ---------------------------------------------------------------------------
# Star animation (mystic style, zero dependencies)
# ---------------------------------------------------------------------------

STAR_CHARS = ["*", ".", "+", "\u00b7", "\u00b0"]  # * . + \xb0


def get_term_size():
    """Return (cols, rows)."""
    try:
        cols, rows = os.get_terminal_size()
        return cols, rows
    except OSError:
        return 80, 24


def random_star(cols, rows):
    return {
        "x": random.randint(0, max(cols - 1, 0)),
        "y": random.randint(0, max(rows - 1, 0)),
        "char": random.choice(STAR_CHARS),
    }


def move_cursor(x, y):
    sys.stdout.write(f"\033[{y};{x}H")


def clear_screen():
    sys.stdout.write("\033[2J")


def reset_colors():
    sys.stdout.write(C.RESET)


def print_at(x, y, text):
    move_cursor(x, y)
    sys.stdout.write(text)


def build_messages(candidates, final):
    """Build the sequence of mystic messages."""
    msgs = [
        "The stars are thinking...",
        "A decision is forming...",
        "The next distro will be decided soon...",
        "Patience is a virtue in the cosmic dance...",
        "The universe is aligning...",
    ]
    for d in candidates:
        name_display = bold_colour(d["name"], d["color"]) if d["bold"] else colour(d["name"], d["color"])
        msgs.append(f"I am thinking about.. {name_display}?")

    msgs.append("A decision has been made..!")

    name_display = bold_colour(final["name"], final["color"]) if final["bold"] else colour(final["name"], final["color"])
    final_msg = f"Your destined distribution is: {name_display}\n{final['desc']}"
    msgs.append(final_msg)

    return msgs


def strip_ansi(text):
    """Remove ANSI codes for length calculations."""
    import re
    return re.sub(r'\033\[[0-9;]*m', '', text)


def play_animation(candidates, final):
    """Render the star-field animation with messages, then keep twinkling until Ctrl+C."""
    cols, rows = get_term_size()
    stars = [random_star(cols, rows) for _ in range(200)]
    messages = build_messages(candidates, final)

    # Phase 1: cycle through messages with animation
    for i, message in enumerate(messages):
        frames = 50 if i == len(messages) - 1 else 20

        for _ in range(frames):
            clear_screen()

            # Draw stars in yellow
            for star in stars:
                print_at(star["x"] + 1, star["y"] + 1, colour(star["char"], C.YELLOW))

            # Draw message centered
            if "\n" in message:
                parts = message.split("\n")
                len0 = len(strip_ansi(parts[0]))
                len1 = len(strip_ansi(parts[1])) if len(parts) > 1 else 0
                px0 = max(cols // 2 - len0 // 2, 0)
                py0 = rows // 2
                px1 = max(cols // 2 - len1 // 2, 0)
                py1 = rows // 2 + 1
                print_at(px0 + 1, py0, parts[0])
                print_at(px1 + 1, py1, parts[1])
            else:
                msg_len = len(strip_ansi(message))
                mx = max(cols // 2 - msg_len // 2, 0)
                print_at(mx + 1, rows // 2, message)

            # Twinkle stars (move slightly)
            for star in stars:
                if random.random() < 0.2:
                    star["x"] = max(0, min(cols - 1, star["x"] + random.randint(-1, 1)))
                    star["y"] = max(0, min(rows - 1, star["y"] + random.randint(-1, 1)))

            # Add occasional new stars
            if random.random() < 0.1 and len(stars) < 250:
                stars.append(random_star(cols, rows))
            # Remove occasional stars
            if random.random() < 0.1 and len(stars) > 40:
                stars.pop(random.randint(0, len(stars) - 1))

            sys.stdout.flush()
            time.sleep(0.1)

    # Phase 2: show final result, keep twinkling until Ctrl+C
    try:
        while True:
            clear_screen()

            for star in stars:
                print_at(star["x"] + 1, star["y"] + 1, colour(star["char"], C.YELLOW))

            # Final message centered
            if "\n" in messages[-1]:
                parts = messages[-1].split("\n")
                len0 = len(strip_ansi(parts[0]))
                len1 = len(strip_ansi(parts[1])) if len(parts) > 1 else 0
                px0 = max(cols // 2 - len0 // 2, 0)
                py0 = rows // 2
                px1 = max(cols // 2 - len1 // 2, 0)
                py1 = rows // 2 + 1
                print_at(px0 + 1, py0, parts[0])
                print_at(px1 + 1, py1, parts[1])
            else:
                msg_len = len(strip_ansi(messages[-1]))
                mx = max(cols // 2 - msg_len // 2, 0)
                print_at(mx + 1, rows // 2, messages[-1])

            # Hint at bottom
            hint = colour("  [Press Ctrl+C to exit]", C.BLACK)
            print_at(1, rows, hint)

            for star in stars:
                if random.random() < 0.2:
                    star["x"] = max(0, min(cols - 1, star["x"] + random.randint(-1, 1)))
                    star["y"] = max(0, min(rows - 1, star["y"] + random.randint(-1, 1)))

            if random.random() < 0.1 and len(stars) < 250:
                stars.append(random_star(cols, rows))
            if random.random() < 0.1 and len(stars) > 40:
                stars.pop(random.randint(0, len(stars) - 1))

            sys.stdout.flush()
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass

    clear_screen()
    reset_colors()


def print_result(cpu, ram_gb, current_os, is_rolling, distro_family, eff_tier, candidates, final, distro_name=None):
    """Print config + recommendation after animation exits."""
    # Reuse print_header for the config section
    print_header(cpu, ram_gb, current_os, is_rolling, distro_family, eff_tier, distro_name)

    final_name = bold_colour(final["name"], final["color"]) if final["bold"] else colour(final["name"], final["color"])
    print(colour("  " + "\u2500" * 50, C.B_BMAGENTA))
    print(colour(f"  {bold('Chosen:')} {final_name}", C.B_BMAGENTA))
    print(f"  {final['desc']}")
    others = [d["name"] for d in candidates if d["name"] != final["name"]]
    if others:
        print(colour(f"  {bold('Also considered:')} {', '.join(others)}", C.B_BCYAN))
    print()


# ---------------------------------------------------------------------------
# Header / system info display
# ---------------------------------------------------------------------------

def print_header(cpu, ram_gb, current_os, is_rolling, distro_family, eff_tier, distro_name=None):
    """Print system info header. Used by both standalone display and post-animation result."""
    print()
    print(colour(f"  distrohoping.py  -  The Stars Decide Your OS  ", C.B_BYELLOW))
    print(colour("  " + "\u2500" * 50, C.B_BCYAN))
    print(f"  {bold('CPU:')} {cpu or 'Unknown'}")
    print(f"  {bold('RAM:')} {ram_gb} GB")

    if current_os == "linux" and distro_name:
        print(f"  {bold('Current OS:')} {colour(distro_name, C.B_BGREEN)} ({current_os})")
    else:
        print(f"  {bold('Current OS:')} {current_os.capitalize()}")

    if current_os == "linux":
        rolling_str = colour("Rolling Release", C.B_BMAGENTA) if is_rolling else colour("Stable / Fixed Release", C.B_BGREEN)
        family_str = distro_family.capitalize() if distro_family != "unknown" else "Unknown"
        print(f"  {bold('Release model:')} {rolling_str}")
        print(f"  {bold('Distro family:')} {family_str}")

    tier_display = {
        "potato": colour("Potato (very old / constrained hardware)", C.B_BRED),
        "light": colour("Light (modest hardware)", C.B_BYELLOW),
        "standard": colour("Standard (average / mid-range and above)", C.B_BGREEN),
    }
    print(f"  {bold('Hardware tier:')} {tier_display.get(eff_tier, eff_tier)}")
    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# CLI argument handling
# ---------------------------------------------------------------------------

def print_help():
    """Print help message."""
    print()
    print(colour(f"  distrohoping.py  -  The Stars Decide Your OS  ", C.B_BYELLOW))
    print(colour("  " + "\u2500" * 50, C.B_BCYAN))
    print(f"  A smart Linux distribution recommender.")
    print()
    print(f"  {bold('Usage:')}")
    print(f"    python3 distrohoping.py                 Detect hardware & recommend with animation")
    print(f"    python3 distrohoping.py --cpu M4 --ram 8  Override detected hardware")
    print(f"    python3 distrohoping.py -h              Show this help message")
    print(f"    python3 distrohoping.py -l              List all distros with descriptions & tiers")
    print()
    print(f"  {bold('Options:')}")
    print(f"    {bold_colour('-h, --help', C.B_BCYAN)}        Show help and exit")
    print(f"    {bold_colour('-l, --list', C.B_BCYAN)}        List all known distros and exit")
    print(f"    {bold_colour('-q, --quiet', C.B_BCYAN)}       Skip the star animation")
    print(f"    {bold_colour('--cpu MODEL', C.B_BCYAN)}       Override detected CPU model string")
    print(f"    {bold_colour('--ram GB', C.B_BCYAN)}          Override detected RAM in GB (integer)")
    print()
    print(f"  {bold('Examples:')}")
    print(f"    python3 distrohoping.py --cpu 'Apple M4' --ram 16")
    print(f"    python3 distrohoping.py --cpu 'BCM2711' --ram 4   # Raspberry Pi 4")
    print(f"    python3 distrohoping.py -q --cpu 'SDM845' --ram 6 # Quiet mode, no animation")
    print()


def list_distros():
    """Print all distros grouped by hardware tier."""
    print()
    print(colour(f"  distrohoping.py  -  All Known Distributions  ", C.B_BYELLOW))
    print(colour("  " + "\u2500" * 50, C.B_BCYAN))
    print()

    tiers = {
        "potato": ("Potato", "Ancient hardware that runs on a potato battery", C.B_BRED),
        "light": ("Light", "Modest hardware (e.g. J4125 / Atom / Celeron)", C.B_BYELLOW),
        "standard": ("Standard", "Average / mid-range and above (i5 / Ryzen 5 and up)", C.B_BGREEN),
    }

    # Group distros by tier
    grouped = {t: [] for t in tiers}
    for d in DISTROS:
        grouped[d["weight"]].append(d)

    for tier_key, (tier_name, tier_desc, tier_color) in tiers.items():
        distros_in_tier = grouped[tier_key]
        if not distros_in_tier:
            continue

        print(colour(f"  {bold(tier_name)} - {tier_desc}", tier_color))
        print(colour("  " + "\u2500" * 50, tier_color))

        for d in distros_in_tier:
            name_display = bold_colour(d["name"], d["color"]) if d["bold"] else colour(d["name"], d["color"])
            print(f"    {name_display}")
            print(f"      {d['desc']}")
            print()

    print(colour(f"  Total: {len(DISTROS)} distributions", C.B_BCYAN))
    print()


def main():
    args = sys.argv[1:]

    # Handle -h/--help and -l/--list
    if "-h" in args or "--help" in args:
        print_help()
        return
    if "-l" in args or "--list" in args:
        list_distros()
        return

    # Parse --cpu, --ram, and --quiet
    cpu_override = None
    ram_override = None
    quiet = False
    i = 0
    while i < len(args):
        if args[i] == "--cpu" and i + 1 < len(args):
            cpu_override = args[i + 1]
            i += 2
        elif args[i] == "--ram" and i + 1 < len(args):
            try:
                ram_override = int(args[i + 1])
            except ValueError:
                print(f"{colour('Invalid --ram value. Use an integer (e.g. --ram 8)', C.B_BRED)}")
                return
            i += 2
        elif args[i] in ("-q", "--quiet"):
            quiet = True
            i += 1
        else:
            i += 1

    try:
        cpu = cpu_override or detect_cpu()
        ram_gb = ram_override if ram_override is not None else detect_ram_gb()
        current_os = detect_current_os()
        is_rolling = detect_is_rolling()
        distro_family = detect_distro_family() if current_os == "linux" else "unknown"
        distro_name = detect_distro_name() if current_os == "linux" else None

        tier = cpu_tier(cpu)
        eff = effective_weight(tier, ram_gb)

        # Brief pause for dramatic effect
        time.sleep(1.0)

        candidates, final = recommend(cpu, ram_gb, current_os, is_rolling, distro_family)

        if not quiet:
            play_animation(candidates, final)

        # Show config + result after animation (or immediately in quiet mode)
        print_result(cpu, ram_gb, current_os, is_rolling, distro_family, eff, candidates, final, distro_name)

    except KeyboardInterrupt:
        print(f"\n{colour('The stars have been interrupted... Try again when the cosmos is ready.', C.B_BYELLOW)}")
    except Exception as e:
        # Graceful fallback: just pick a random distro
        print(f"\n{colour('Something went wrong with the cosmic alignment...', C.B_BRED)}")
        print(f"{colour(f'Error: {e}', C.B_BRED)}")
        print(f"{colour('Falling back to random selection...', C.B_BYELLOW)}")
        fallback = random.choice(DISTROS)
        name_display = bold_colour(fallback["name"], fallback["color"]) if fallback["bold"] else colour(fallback["name"], fallback["color"])
        print(f"\n{colour('The stars say:', C.B_BMAGENTA)} {name_display}")
        print(f"{fallback['desc']}")


if __name__ == "__main__":
    main()
