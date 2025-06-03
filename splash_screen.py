import tkinter as tk

class SplashScreen(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.overrideredirect(True)
        self.border_color = "#00adb5"   # Border color
        self.bg_color = "#23272f"       # Main background color
        self.width = 560
        self.height = 400

        # Center the splash screen
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (self.width // 2)
        y = (screen_height // 2) - (self.height // 2)
        self.geometry(f"{self.width}x{self.height}+{x}+{y}")
        self.configure(bg=self.border_color)
        self.attributes('-alpha', 0.0)  # Start transparent for fade-in

        # Create a frame inside to act as the main content area with padding (border thickness)
        border_thickness = 6
        self.content_frame = tk.Frame(self, bg=self.bg_color)
        self.content_frame.place(
            x=border_thickness, y=border_thickness,
            width=self.width - 2*border_thickness,
            height=self.height - 2*border_thickness
        )

        # App name (typewriter animation)
        self.app_name = "TrackEdge"
        self.label = tk.Label(self.content_frame, text="", font=("Segoe UI", 44, "bold"), fg="#00adb5", bg=self.bg_color)
        self.label.pack(pady=(55, 10))

        # Tagline
        self.tagline = tk.Label(
            self.content_frame, text="Your Business, Sharper.",
            font=("Segoe UI", 16, "italic"), fg="#eeeeee", bg=self.bg_color
        )
        self.tagline.pack(pady=(0, 16))

        # Animated loader dots
        self.loader_frame = tk.Frame(self.content_frame, bg=self.bg_color)
        self.loader_frame.pack(pady=(18, 0))
        self.dots = []
        for i in range(3):
            dot = tk.Label(self.loader_frame, text="●", font=("Segoe UI", 22, "bold"), fg="#393e46", bg=self.bg_color)
            dot.grid(row=0, column=i, padx=8)
            self.dots.append(dot)
        self.loader_step = 0

        # Features
        features = [
            "• Track daily sales",
            "• Manage services & purchases",
            "• Smart notifications",
            "• Inventory at a glance"
        ]
        self.features_label = tk.Label(
            self.content_frame, text="\n".join(features),
            font=("Segoe UI", 11), fg="#bdbdbd", bg=self.bg_color, justify="left"
        )
        self.features_label.pack(pady=(18, 0))

        # Animation settings
        self.fade_in_step = 0.06
        self.fade_out_step = 0.08

        # Start animations
        self.after(0, self.fade_in)
        self.after(200, self.typewriter_effect, 0)
        self.after(0, self.animate_loader)

    def fade_in(self):
        alpha = self.attributes('-alpha')
        if alpha < 1.0:
            alpha = min(alpha + self.fade_in_step, 1.0)
            self.attributes('-alpha', alpha)
            self.after(40, self.fade_in)

    def fade_out(self, callback=None):
        alpha = self.attributes('-alpha')
        if alpha > 0.0:
            alpha = max(alpha - self.fade_out_step, 0.0)
            self.attributes('-alpha', alpha)
            self.after(40, lambda: self.fade_out(callback))
        else:
            if callback:
                callback()

    def typewriter_effect(self, idx):
        if idx <= len(self.app_name):
            self.label.config(text=self.app_name[:idx])
            self.after(90, self.typewriter_effect, idx+1)

    def animate_loader(self):
        # Animate glowing loader dots
        for i, dot in enumerate(self.dots):
            if i == self.loader_step % 3:
                dot.config(fg="#00adb5")
            else:
                dot.config(fg="#393e46")
        self.loader_step += 1
        self.after(250, self.animate_loader)

# Example usage (main.py):
if __name__ == "__main__":
    def main():
        root = tk.Tk()
        root.withdraw()  # Hide main window initially

        splash = SplashScreen(root)
        splash.update()  # Show splash instantly

        def show_main_app():
            splash.fade_out(lambda: [
                splash.destroy(),
                root.deiconify()
                # Initialize your main app here, e.g.:
                # app = TrackedgeApp(root)
            ])

        # Show splash for 2.4 seconds before starting fade out
        root.after(2400, show_main_app)
        root.mainloop()

    main()
