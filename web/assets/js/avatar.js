// avatarGenerator.js

// Simple seeded pseudo-random number generator (PRNG)
function mulberry32(seed) {
    let _seed = typeof seed === 'string' ? hashString(seed) : seed;
    return function() {
        _seed = _seed + 0x6D2B79F5 | 0;
        let t = Math.imul(_seed ^ _seed >>> 15, 1 | _seed);
        t = t + Math.imul(t ^ t >>> 7, 61 | t) | 0;
        return ((t ^ t >>> 14) >>> 0) / 4294967296;
    }
}

// Simple string hash function for seeding
function hashString(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
        hash = str.charCodeAt(i) + ((hash << 5) - hash);
    }
    return hash;
}

/**
         * Generates a random color for Space Invader features using a seeded RNG.
         * @param {function} rng - The seeded random number generator function.
         * @returns {string} A string representing a random hex color.
         */
        function getInvaderColor(rng) {
            const invaderColors = [
                 '#FFDAB9', // Peach (skin)
                '#E0BBE4', // Light Pinkish-Purple (skin/clothing)
                '#C0C0C0', // Silver (gray hair/clothing)
                '#8B4513', // SaddleBrown (brown hair)
                '#2F4F4F', // DarkSlateGray (dark hair/clothing)
                '#000000', // Black (eyes/dark details)
                '#FFFFFF'  // White (eyes/highlights)
            ];
            return invaderColors[Math.floor(rng() * invaderColors.length)];
        }

        /**
         * Generates and draws a minimal pixelated Space Invader avatar on the canvas.
         * This function is designed to be globally accessible.
         * @param {HTMLCanvasElement} canvasElement - The canvas to draw on.
         * @param {string} seed - A string (e.g., conversation ID) to seed the random generation.
         */
        function generateAvatar(canvasElement, seed) {
            const ctx = canvasElement.getContext('2d');
            const RNG = mulberry32(seed); // Initialize RNG with seed

            const CANVAS_SIZE = 50;
            canvasElement.width = CANVAS_SIZE;
            canvasElement.height = CANVAS_SIZE;

            const GRID_SIZE = 8;
            const PIXEL_SIZE = CANVAS_SIZE / GRID_SIZE;

            /**
             * Draws a single conceptual pixel (square) on the canvas.
             * @param {number} col - The column index in the GRID_SIZE.
             * @param {number} row - The row index in the GRID_SIZE.
             * @param {string} color - The fill color for the pixel.
             */
            function drawConceptualPixel(col, row, color) {
                const drawX = col * PIXEL_SIZE;
                const drawY = row * PIXEL_SIZE;
                ctx.fillStyle = color;
                ctx.fillRect(drawX, drawY, PIXEL_SIZE, PIXEL_SIZE);
            }

            // Clear the entire canvas
            ctx.clearRect(0, 0, CANVAS_SIZE, CANVAS_SIZE);

            // Create a 2D array to store the state and color of each conceptual pixel
            const pixelMap = Array(GRID_SIZE).fill(0).map(() => Array(GRID_SIZE).fill(null));

            // Define base colors for the avatar using the seeded RNG
            const mainBodyColor = getInvaderColor(RNG);
            const eyeColor = getInvaderColor(RNG);
            const detailColor = getInvaderColor(RNG);

            // Ensure eyeColor is distinct from mainBodyColor
            let safeEyeColor = eyeColor;
            while (safeEyeColor === mainBodyColor) {
                safeEyeColor = getInvaderColor(RNG);
            }

            // --- Generate the Invader's shape ---
            for (let row = 0; row < GRID_SIZE; row++) {
                for (let col = 0; col < Math.ceil(GRID_SIZE / 2); col++) { // Iterate only up to the middle
                    let colorToApply = null;

                    // Define a classic Space Invader shape
                    // Top head/body
                    if (row === 0 && (col === 2 || col === 3)) { // Top antennae/horns
                        colorToApply = mainBodyColor;
                    } else if (row === 1 && (col >= 1 && col <= 3)) {
                        colorToApply = mainBodyColor;
                    } else if (row === 2 && (col >= 0 && col <= 3)) {
                        colorToApply = mainBodyColor;
                    }
                    // Middle body section
                    else if (row === 3 && (col >= 0 && col <= 3)) {
                        colorToApply = mainBodyColor;
                    }
                    // Lower body/legs
                    else if (row === 4 && (col >= 0 && col <= 3)) {
                         if (col === 0 || col === 3) { // Outer legs
                            colorToApply = mainBodyColor;
                        } else if (RNG() < 0.5) { // Random internal body
                             colorToApply = mainBodyColor;
                        }
                    } else if (row === 5 && (col === 0 || col === 3)) { // Lower legs
                        colorToApply = mainBodyColor;
                    }
                     else if (row === 6 && (col === 1 || col === 2)) { // Feet/tentacles
                        colorToApply = mainBodyColor;
                    }


                    // Store the color for both left and mirrored right half
                    if (colorToApply) {
                        pixelMap[row][col] = colorToApply;
                        pixelMap[row][GRID_SIZE - 1 - col] = colorToApply;
                    } else {
                        pixelMap[row][col] = null;
                        pixelMap[row][GRID_SIZE - 1 - col] = null;
                    }
                }
            }

            // --- Add specific features (eyes) ---
            // Eyes
            const eyeRow = 2;
            const eyeColOffset = 1; // Offset from center
            pixelMap[eyeRow][Math.floor(GRID_SIZE / 2) - eyeColOffset] = safeEyeColor;     // Left eye
            pixelMap[eyeRow][Math.floor(GRID_SIZE / 2) + eyeColOffset - 1] = safeEyeColor; // Right eye

            // Optional: Add some random internal detail for variation
            for (let r = 1; r < GRID_SIZE - 1; r++) {
                for (let c = 1; c < GRID_SIZE - 1; c++) {
                    if (pixelMap[r][c] === mainBodyColor && RNG() < 0.05) { // Small chance to add internal pixel detail
                        pixelMap[r][c] = detailColor;
                    }
                }
            }


            // --- Draw the pixels based on the generated map ---
            for (let row = 0; row < GRID_SIZE; row++) {
                for (let col = 0; col < GRID_SIZE; col++) {
                    const color = pixelMap[row][col];
                    if (color) {
                        drawConceptualPixel(col, row, color);
                    }
                }
            }
        }
