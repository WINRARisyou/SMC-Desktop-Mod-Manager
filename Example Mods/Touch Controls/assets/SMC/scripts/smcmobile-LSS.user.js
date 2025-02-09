/* WINRARisyou was here. */
window.CONTROLS_VERSION = "1.0.5"
window.debugmode = false;
// reset controls
window.reset = true;

// draw from public/game/ folder
window.assetsURL = "/TouchControls";

function initTouchControls(mobile) {
    if (window.TouchControlsLoaded && window.reset == false) {
        console.warn("Touch Controls have already been created! Don't make 'em twice!");
        return;
    }
    if (mobile) {
        // do nothing.
    } else {
        var onPC = prompt("You are not on a mobile/touch device. Do you want to delete touch Controls?", "Yes/No")
        if (!onPC) { initTouchControls(); return; }
        if (onPC.toLowerCase().includes("y")) {
            return;
        } else if (onPC.toLowerCase().includes("n")) {
            // continue execution
        }

    }
    window.reset = false;
    window.TouchControlsLoaded = true;
    const gamepadConfig = {
        specialButtons: {
            position: { top: "0px", left: "0px" },
            size: { width: "100%", height: "30px" },
            buttons: [
                { id: "pause", border: true, label: "Pause", color1: "rgba(255, 255, 255, 0.5)", color2: "rgba(255, 255, 0, 0.5)", x: "calc(50% - 65px)", y: "0px", width: "60px", height: "30px", key: "p", keyCode: 80 },
                { id: "fullscreen", border: true, label: "Fullscreen", color1: "rgba(255, 255, 255, 0.5)", color2: "rgba(255, 255, 0, 0.5)", x: "calc(50% + 5px)", y: "0px", width: "90px", height: "30px", key: "", keyCode: 0 },
                { id: "item", border: true, label: "Item", color1: "rgba(255, 255, 255, 0.5)", color2: "rgba(255, 255, 0, 0.5)", x: "calc(50% - 30px)", y: "35px", width: "60px", height: "60px", key: "Shift", keyCode: 16 }
            ]
        },
        dpad: {
            position: { bottom: 60, left: 10 },
            size: { width: 150, height: 150 },
            buttons: [
                { id: "up", label: "↑", border: false, color1: "rgba(255, 255, 255, 0)", color2: "rgba(255, 255, 0, 0)", active: "up-active.png", inactive: "up-inactive.png", x: 50, y: 0, width: 50, height: 50, key: "ArrowUp", keyCode: 38 },
                { id: "left", label: "←", border: false, color1: "rgba(255, 255, 255, 0)", color2: "rgba(255, 255, 0, 0)", active: "left-active.png", inactive: "left-inactive.png", x: 0, y: 50, width: 50, height: 50, key: "ArrowLeft", keyCode: 37 },
                { id: "right", label: "→", border: false, color1: "rgba(255, 255, 255, 0)", color2: "rgba(255, 255, 0, 0)", active: "right-active.png", inactive: "right-inactive.png", x: 100, y: 50, width: 50, height: 50, key: "ArrowRight", keyCode: 39 },
                { id: "down", label: "↓", border: false, color1: "rgba(255, 255, 255, 0)", color2: "rgba(255, 255, 0, 0)", active: "down-active.png", inactive: "down-inactive.png", x: 50, y: 100, width: 50, height: 50, key: "ArrowDown", keyCode: 40 },
                { id: "center", label: "", border: false, color1: "rgba(255, 255, 255, 0)", color2: "rgba(255, 255, 0, 0)", active: "center.png", inactive: "center.png", x: 50, y: 50, width: 50, height: 50, key: "", keyCode: 0 }
            ]
        },
        actionButtons: {
            position: { bottom: 60, right: 10 },
            size: { width: 200, height: 130 },
            buttons: [
                { id: "jump", label: "Jump", border: false, color1: "rgba(255, 255, 255, 0)", color2: "rgba(255, 255, 0, 0)", active: "B-active.png", inactive: "B-inactive.png", x: 0, y: 70, width: 60, height: 60, key: "z", keyCode: 90 },
                { id: "run", label: "Run", border: false, color1: "rgba(255, 255, 255, 0)", color2: "rgba(255, 255, 0, 0)", active: "Y-active.png", inactive: "Y-inactive.png", x: 70, y: 70, width: 60, height: 60, key: "x", keyCode: 88 },
                { id: "spinjump", label: "Spin", border: false, color1: "rgba(255, 255, 255, 0)", color2: "rgba(255, 255, 0, 0)", active: "A-active.png", inactive: "A-inactive.png", x: 140, y: 70, width: 60, height: 60, key: "c", keyCode: 67 },
                { id: "usepowerup", label: "Use Powerup", border: false, color1: "rgba(255, 255, 255, 0)", color2: "rgba(255, 255, 0, 0)", active: "X-active.png", inactive: "X-inactive.png", x: 105, y: 0, width: 60, height: 60, key: " ", keyCode: 32 },
                { id: "togglerun", label: "Toggle Run", border: true, color1: "rgba(255, 255, 255, 0.5)", color2: "rgba(255, 255, 0, 0.5)", x: 35, y: 0, width: 60, height: 60, key: "x", keyCode: 88, isToggle: true }
            ]
        }
    };

    function createButton(button, container) {
        const elem = document.createElement("button");
        elem.id = button.id;
        elem.textContent = button.label;
        elem.style.position = "absolute";
        if (container.id != "special") {
            elem.style.left = `${button.x}px`;
            elem.style.top = `${button.y}px`;
            elem.style.width = `${button.width}px`;
            elem.style.height = `${button.height}px`;
        } else {
            elem.style.left = `${button.x}`;
            elem.style.top = `${button.y}`;
            elem.style.width = `${button.width}`;
            elem.style.height = `${button.height}`;
        }
        elem.style.backgroundSize = "cover"
        elem.style.backgroundImage = `url("${window.assetsURL}/${button.inactive}")`
        elem.style.backgroundColor = button.color1;
        elem.setAttribute("onclick", "event.stopImmediatePropagation();event.stopPropagation();event.preventDefault()")
        elem.style.border = "1px solid black";
        if (button.border) {
            elem.style.borderRadius = "5px";
        } else {
            elem.style.border = "none";
        }
        elem.style.fontSize = "14px";
        elem.style.userSelect = "none";
        container.appendChild(elem);
        return elem;
    }

    let toggledButtons = new Set();

    function createGamepad() {
        const gamepad = document.createElement("div");
        const gameFrame = document.getElementById("game-wrapper");
        gamepad.id = "touch-gamepad";
        gamepad.style.position = "fixed";
        gamepad.style.zIndex = "9998";
        gamepad.style.pointerEvents = "none";
        gamepad.style.width = "100%";
        gamepad.style.height = "100%";
        gamepad.style.top = "0px";
        gamepad.style.left = "0px"
        gameFrame.appendChild(gamepad);

        const special = document.createElement("div")
        special.id = "special"
        special.style.position = "absolute";
        special.style.width = `${gamepadConfig.specialButtons.size.width}`;
        special.style.height = `${gamepadConfig.specialButtons.size.height}`;
        special.style.top = `${gamepadConfig.specialButtons.position.top}`;
        special.style.left = `${gamepadConfig.specialButtons.position.left}`;
        special.style.pointerEvents = "auto";
        if (window.debugmode) {
            special.style.backgroundColor = "rgba(0, 255, 0, 0.2)";
        }
        gamepad.appendChild(special);

        const dpad = document.createElement("div");
        dpad.id = "dpad";
        dpad.style.position = "absolute";
        dpad.style.width = `${gamepadConfig.dpad.size.width}px`;
        dpad.style.height = `${gamepadConfig.dpad.size.height}px`;
        dpad.style.bottom = `${gamepadConfig.dpad.position.bottom}px`;
        dpad.style.left = `${gamepadConfig.dpad.position.left}px`;
        dpad.style.pointerEvents = "auto";
        if (window.debugmode) {
            dpad.style.backgroundColor = "rgba(0, 0, 255, 0.2)";
        }
        gamepad.appendChild(dpad);

        const actionButtons = document.createElement("div");
        actionButtons.id = "action-buttons";
        actionButtons.style.position = "absolute";
        actionButtons.style.width = `${gamepadConfig.actionButtons.size.width}px`;
        actionButtons.style.height = `${gamepadConfig.actionButtons.size.height}px`;
        actionButtons.style.bottom = `${gamepadConfig.actionButtons.position.bottom}px`;
        actionButtons.style.right = `${gamepadConfig.actionButtons.position.right}px`;
        actionButtons.style.pointerEvents = "auto";
        if (window.debugmode) {
            actionButtons.style.backgroundColor = "rgba(255, 0, 0, 0.2)";
        }
        gamepad.appendChild(actionButtons);

        const buttons = {};

        gamepadConfig.specialButtons.buttons.forEach(button => {
            const elem = createButton(button, special);
            buttons[button.id] = { ...button, element: elem };
        });

        gamepadConfig.dpad.buttons.forEach(button => {
            const elem = createButton(button, dpad);
            buttons[button.id] = { ...button, element: elem };
        });

        gamepadConfig.actionButtons.buttons.forEach(button => {
            const elem = createButton(button, actionButtons);
            buttons[button.id] = { ...button, element: elem };
        });

        // Debug information
        if (window.debugmode == true) {
            const debugInfo = document.createElement("div");
            debugInfo.id = "debug-info";
            debugInfo.style.position = "fixed";
            debugInfo.style.top = "10px";
            debugInfo.style.left = "10px";
            debugInfo.style.backgroundColor = "rgba(0, 0, 0, 0.7)";
            debugInfo.style.color = "white";
            debugInfo.style.padding = "10px";
            debugInfo.style.fontFamily = "monospace";
            debugInfo.style.fontSize = "12px";
            debugInfo.style.zIndex = "999999";
            document.body.appendChild(debugInfo);

            updateDebugInfo();
        }

        return buttons;
    }

    function updateDebugInfo() {
        const gamepad = document.getElementById("touch-gamepad");
        const dpad = document.getElementById("dpad");
        const actionButtons = document.getElementById("action-buttons");
        const debugInfo = document.getElementById("debug-info");


        debugInfo.innerHTML = `
            Gamepad: ${gamepad.offsetWidth}x${gamepad.offsetHeight}<br>
            D-pad: ${dpad.offsetLeft},${dpad.offsetTop} ${dpad.offsetWidth}x${dpad.offsetHeight}<br>
            Action: ${actionButtons.offsetLeft},${actionButtons.offsetTop} ${actionButtons.offsetWidth}x${actionButtons.offsetHeight}
        `;
    }

    const buttons = createGamepad();

    let activeButtons = new Set();
    let touchMap = new Map();
    let activeButtonStates = {};

    function simulateKeyEvent(keyInfo, type) {
        const iframe = document.getElementById("game"); // Get the iframe
        if (!iframe || !iframe.contentWindow) {
            console.error("Iframe not found or inaccessible.");
            return;
        }
        let iframeDocument = iframe.contentWindow.document;

        let event;
        event = new KeyboardEvent(type, {
            bubbles: true,
            cancelable: true,
            key: keyInfo.key,
            keyCode: keyInfo.keyCode,
            which: keyInfo.keyCode,
            code: `Key${keyInfo.key.toUpperCase()}`,
        });

        const originalPreventDefault = event.preventDefault.bind(event);
        event.preventDefault = function () {
            if (type === "keydown") {
                event.defaultPrevented = true;
            }
            originalPreventDefault();
        };

        document.dispatchEvent(event);
        window.dispatchEvent(event);
        iframeDocument.dispatchEvent(event);

        if (type === "keydown" && !event.defaultPrevented) {
            simulateKeyEvent(keyInfo, "keypress");
        }
    }

    function handleButtonPress(button) {
        const currentButton = buttons[button];
        const key = currentButton.key;
        if (button === "fullscreen") {
            const iframe = document.getElementById("game-wrapper");
            if (iframe.requestFullscreen) return iframe.requestFullscreen();
            if (iframe.webkitRequestFullscreen) return iframe.webkitRequestFullscreen();
        }
        if (currentButton.isToggle) {
            if (toggledButtons.has(button)) {
                toggledButtons.delete(button);
                activeButtonStates[key] = false;
                currentButton.element.style.backgroundColor = currentButton.color1;
                currentButton.element.style.backgroundImage = `url("${window.assetsURL}/${currentButton.inactive}")`;
                simulateKeyEvent(currentButton, "keyup");
            } else {
                toggledButtons.add(button);
                activeButtonStates[key] = true;
                currentButton.element.style.backgroundColor = currentButton.color2;
                currentButton.element.style.backgroundImage = `url("${window.assetsURL}/${currentButton.active}")`;
                simulateKeyEvent(currentButton, "keydown");
            }
        } else {
            // If the button is not a toggle, we should only simulate the keydown if it"s not already active
            if (!activeButtons.has(button) && !activeButtonStates[key]) {
                activeButtons.add(button);
                activeButtonStates[key] = true;
                currentButton.element.style.backgroundColor = currentButton.color2;
                currentButton.element.style.backgroundImage = `url("${window.assetsURL}/${currentButton.active}")`;
                simulateKeyEvent(currentButton, "keydown");
            }
        }
    }

    function handleButtonRelease(button) {
        const currentButton = buttons[button];
        const key = currentButton.key;

        if (!currentButton.isToggle) {
            if (activeButtons.has(button)) {
                activeButtons.delete(button);
                activeButtonStates[key] = false;
                simulateKeyEvent(currentButton, "keyup");
                currentButton.element.style.backgroundColor = currentButton.color1;
                currentButton.element.style.backgroundImage = `url("${window.assetsURL}/${currentButton.inactive}")`;
            }
        }
    }

    function handleTouchStart(event) {
        event.preventDefault();
        Array.from(event.changedTouches).forEach(touch => {
            const element = document.elementFromPoint(touch.clientX, touch.clientY);
            const button = element.id;
            if (button in buttons) {
                touchMap.set(touch.identifier, button);
                handleButtonPress(button);
            }
        });
    }

    function handleTouchMove(event) {
        event.preventDefault();
        Array.from(event.changedTouches).forEach(touch => {
            const element = document.elementFromPoint(touch.clientX, touch.clientY);
            const newButton = element.id;
            const oldButton = touchMap.get(touch.identifier);

            if (oldButton !== newButton) {
                if (oldButton in buttons) {
                    handleButtonRelease(oldButton);
                }
                if (newButton in buttons) {
                    touchMap.set(touch.identifier, newButton);
                    handleButtonPress(newButton);
                } else {
                    touchMap.delete(touch.identifier);
                }
            }
        });
    }

    function handleTouchEnd(event) {
        event.preventDefault();
        Array.from(event.changedTouches).forEach(touch => {
            const button = touchMap.get(touch.identifier);
            if (button) {
                handleButtonRelease(button);
                touchMap.delete(touch.identifier);
            }
        });
    }

    const gamepad = document.getElementById("touch-gamepad");
    gamepad.addEventListener("touchstart", handleTouchStart, { passive: false });
    gamepad.addEventListener("touchmove", handleTouchMove, { passive: false });
    gamepad.addEventListener("touchend", handleTouchEnd, { passive: false });
    gamepad.addEventListener("touchcancel", handleTouchEnd, { passive: false });

    // Update debug info on window resize
    if (window.debugmode)
        window.addEventListener("resize", updateDebugInfo);

}

window.resetWithDebug = function resetWithDebug() {
    var gamepad = document.getElementById("touch-gamepad");
    if (gamepad != undefined) {
        gamepad.remove();
    }
    var debug = document.getElementById("debug-info");
    if (debug != undefined) {
        debug.remove();
    }
    window.debugmode = true;
    window.reset = true;
    initTouchControls();
}

window.resetControls = function resetControls() {
    var gamepad = document.getElementById("touch-gamepad");
    if (gamepad != undefined) {
        gamepad.remove();
    }
    var debug = document.getElementById("debug-info");
    if (debug != undefined) {
        debug.remove();
    }
    window.debugmode = false;
    window.reset = true;
    initTouchControls();
}

window.deleteControls = function deleteControls() {
    var gamepad = document.getElementById("touch-gamepad");
    if (gamepad != undefined) {
        gamepad.remove();
    }
    var debug = document.getElementById("debug-info");
    if (debug != undefined) {
        debug.remove();
    }
}

initTouchControls(true);
/* WINRARisyou was here. */
// TFD was here too