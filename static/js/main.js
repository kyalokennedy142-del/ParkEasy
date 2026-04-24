document.addEventListener("DOMContentLoaded", () => {
    // Form submission feedback
    document.querySelectorAll("form").forEach(form => {
        form.addEventListener("submit", function() {
            const btn = this.querySelector("button[type='submit']");
            if (btn) {
                btn.textContent = "Processing...";
                btn.disabled = true;
            }
        });
    });

    // Auto-dismiss flash messages after 4 seconds
    document.querySelectorAll('.flash').forEach(flash => {
        setTimeout(() => {
            flash.style.opacity = '0';
            flash.style.transform = 'translateY(-10px)';
            setTimeout(() => flash.remove(), 300);
        }, 4000);
    });

    initParkingMap();
});

function initParkingMap() {
    const mapElement = document.getElementById("parking-leaflet-map");
    const slotDataElement = document.getElementById("parking-slot-data");
    const centerDataElement = document.getElementById("parking-map-center-data");

    if (!mapElement || !slotDataElement || !centerDataElement || !window.L) {
        return;
    }

    const slots = JSON.parse(slotDataElement.textContent || "[]");
    const center = JSON.parse(centerDataElement.textContent || "{}");
    const map = L.map(mapElement, {
        scrollWheelZoom: true,
    });
    map.setView([center.lat, center.lng], 19);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 20,
    }).addTo(map);

    const bounds = L.latLngBounds([]);

    slots.forEach((slot) => {
        const markerState = slot.recommended ? "recommended" : slot.status;
        const marker = L.marker([slot.lat, slot.lng], {
            icon: L.divIcon({
                className: "parking-marker-wrapper",
                html: `<div class="parking-marker ${markerState}"><span>${slot.slot_number}</span><small>${slot.status === "available" ? "Free" : "Taken"}</small></div>`,
                iconSize: [54, 52],
                iconAnchor: [27, 26],
                popupAnchor: [0, -28],
            }),
        });

        marker.bindPopup(`
            <div class="map-info-window">
                <h4>${slot.slot_number}</h4>
                <p>${slot.zone} - Row ${slot.row}</p>
                <p>Status: ${slot.status}</p>
                <p>${slot.status === "available" ? "Ready to book now." : `Booked by: ${slot.booked_by || "Unknown"}`}</p>
            </div>
        `);
        marker.addTo(map);

        bounds.extend([slot.lat, slot.lng]);
    });

    if (slots.length) {
        map.fitBounds(bounds, { padding: [40, 40] });
    }
}
