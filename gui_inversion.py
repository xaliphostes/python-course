import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import threading

from mylib import costStylos, costVeins, Remote, openFractureFile


class InversionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Paleostress Inversion")
        self.root.minsize(900, 650)

        self.veins_path = tk.StringVar()
        self.stylo_path = tk.StringVar()
        self.num_iter = tk.IntVar(value=10000)
        self.cmap_name = tk.StringVar(value='viridis')
        self.running = False

        # store last results for live colormap update
        self._last_result = None

        self._build_ui()

    def _build_ui(self):
        # --- Top: file selection and parameters ---
        top = ttk.LabelFrame(self.root, text="Parameters", padding=8)
        top.pack(fill=tk.X, padx=8, pady=(8, 4))

        ttk.Label(top, text="Veins file:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(top, textvariable=self.veins_path, width=50).grid(row=0, column=1, padx=4)
        ttk.Button(top, text="Browse…", command=lambda: self._browse(self.veins_path)).grid(row=0, column=2)

        ttk.Label(top, text="Stylolites file:").grid(row=1, column=0, sticky=tk.W)
        ttk.Entry(top, textvariable=self.stylo_path, width=50).grid(row=1, column=1, padx=4)
        ttk.Button(top, text="Browse…", command=lambda: self._browse(self.stylo_path)).grid(row=1, column=2)

        ttk.Label(top, text="Iterations:").grid(row=2, column=0, sticky=tk.W)
        ttk.Entry(top, textvariable=self.num_iter, width=12).grid(row=2, column=1, sticky=tk.W, padx=4)

        cmaps = ['viridis', 'plasma', 'inferno', 'magma', 'cividis',
                 'hot', 'coolwarm', 'Spectral', 'RdYlBu', 'terrain', 'jet']
        ttk.Label(top, text="Colormap:").grid(row=3, column=0, sticky=tk.W)
        cmap_combo = ttk.Combobox(top, textvariable=self.cmap_name, values=cmaps, width=14, state='readonly')
        cmap_combo.grid(row=3, column=1, sticky=tk.W, padx=4)
        cmap_combo.bind('<<ComboboxSelected>>', lambda _: self._update_cmap())

        self.run_btn = ttk.Button(top, text="Run Inversion", command=self._run)
        self.run_btn.grid(row=2, column=2, padx=4)

        # --- Results bar ---
        res = ttk.LabelFrame(self.root, text="Results", padding=8)
        res.pack(fill=tk.X, padx=8, pady=4)

        self.result_var = tk.StringVar(value="No results yet.")
        ttk.Label(res, textvariable=self.result_var, font=("Courier", 13)).pack(anchor=tk.W)

        self.progress = ttk.Progressbar(res, mode='determinate')
        self.progress.pack(fill=tk.X, pady=(4, 0))

        # --- Matplotlib figure ---
        fig_frame = ttk.Frame(self.root)
        fig_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=(4, 8))

        self.fig = Figure(figsize=(9, 4), tight_layout=True)
        self.ax_domain = self.fig.add_subplot(121)
        self.ax_domain.set_title("Cost domain")
        self.ax_domain.set_xlabel("R")
        self.ax_domain.set_ylabel("Theta (°)")

        self.ax_hist = self.fig.add_subplot(122)
        self.ax_hist.set_title("Cost per fracture type")

        self.canvas = FigureCanvasTkAgg(self.fig, master=fig_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _browse(self, var):
        path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if path:
            var.set(path)

    def _run(self):
        if self.running:
            return
        vp = self.veins_path.get().strip()
        sp = self.stylo_path.get().strip()
        if not vp or not sp:
            messagebox.showwarning("Missing files", "Please select both veins and stylolites files.")
            return
        try:
            n = self.num_iter.get()
            if n <= 0:
                raise ValueError
        except (tk.TclError, ValueError):
            messagebox.showwarning("Invalid iterations", "Please enter a positive integer for iterations.")
            return

        self.running = True
        self.run_btn.config(state=tk.DISABLED)
        self.result_var.set("Running…")
        self.progress['value'] = 0

        threading.Thread(target=self._inversion_thread, args=(vp, sp, n), daemon=True).start()

    def _inversion_thread(self, veins_path, stylo_path, num_iter):
        try:
            veins = openFractureFile(veins_path)
            stylolites = openFractureFile(stylo_path)
        except Exception as e:
            self.root.after(0, lambda: self._on_error(f"Error loading files:\n{e}"))
            return

        min_cost = float('inf')
        best_theta = 0.0
        best_R = 0.0
        step = max(1, num_iter // 100)

        for i in range(num_iter):
            theta = np.random.uniform(0, 180)
            R = np.random.uniform(0, 1)
            remote = Remote(theta, R)
            c = (costStylos(stylolites, remote) + costVeins(veins, remote)) / 2
            if c < min_cost:
                min_cost = c
                best_theta = theta
                best_R = R
            if i % step == 0:
                pct = i / num_iter * 100
                self.root.after(0, lambda p=pct: self.progress.configure(value=p))

        self.root.after(0, lambda: self.progress.configure(value=100))
        self.root.after(0, lambda: self._show_results(veins, stylolites, best_theta, best_R, min_cost))

    def _show_results(self, veins, stylolites, best_theta, best_R, min_cost):
        fit = (1 - min_cost) * 100
        self.result_var.set(
            f"θ = {best_theta:.1f}°    R = {best_R:.3f}    cost = {min_cost:.3f}    fit = {fit:.1f}%"
        )

        # --- Compute domain cost map ---
        nR, nTheta = 50, 90
        Rs = np.linspace(0, 1, nR)
        thetas = np.linspace(0, 180, nTheta)
        cost_map = np.zeros((nTheta, nR))
        for i, th in enumerate(thetas):
            for j, r in enumerate(Rs):
                remote = Remote(th, r)
                cost_map[i, j] = (costStylos(stylolites, remote) + costVeins(veins, remote)) / 2

        # --- Plot per-type costs ---
        remote = Remote(best_theta, best_R)
        cost_v = costVeins(veins, remote)
        cost_s = costStylos(stylolites, remote)

        # --- Save for live colormap update ---
        self._last_result = dict(cost_map=cost_map, Rs=Rs, thetas=thetas,
                                 best_theta=best_theta, best_R=best_R, min_cost=min_cost,
                                 cost_v=cost_v, cost_s=cost_s)

        # --- Plot domain ---
        self.ax_domain.clear()
        im = self.ax_domain.imshow(cost_map, extent=[0, 1, 0, 180], origin='lower', aspect='auto', cmap=self.cmap_name.get())
        self.ax_domain.contour(Rs, thetas, cost_map, levels=10, colors='white', linewidths=0.5)
        self.ax_domain.plot(best_R, best_theta, 'r*', markersize=15,
                           label=f'Best (θ={best_theta:.1f}°, R={best_R:.3f})')
        self.ax_domain.set_xlabel('R')
        self.ax_domain.set_ylabel('Theta (°)')
        self.ax_domain.set_title('Cost domain')
        self.ax_domain.legend(fontsize=8)

        self.ax_hist.clear()
        bars = self.ax_hist.bar(['Veins', 'Stylolites', 'Combined'], [cost_v, cost_s, min_cost], color=['#4c72b0', '#dd8452', '#55a868'])
        self.ax_hist.set_ylabel('Cost')
        self.ax_hist.set_ylim(0, max(cost_v, cost_s, min_cost) * 1.3 + 0.01)
        self.ax_hist.set_title('Cost per fracture type')
        for bar, val in zip(bars, [cost_v, cost_s, min_cost]):
            self.ax_hist.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.005,
                              f'{val:.3f}', ha='center', fontsize=9)

        self.canvas.draw()
        self.running = False
        self.run_btn.config(state=tk.NORMAL)

    def _update_cmap(self):
        if self._last_result is None:
            return
        d = self._last_result
        self.ax_domain.clear()
        self.ax_domain.imshow(d['cost_map'], extent=[0, 1, 0, 180], origin='lower', aspect='auto',
                              cmap=self.cmap_name.get())
        self.ax_domain.contour(d['Rs'], d['thetas'], d['cost_map'], levels=10, colors='white', linewidths=0.5)
        self.ax_domain.plot(d['best_R'], d['best_theta'], 'r*', markersize=15,
                            label=f"Best (θ={d['best_theta']:.1f}°, R={d['best_R']:.3f})")
        self.ax_domain.set_xlabel('R')
        self.ax_domain.set_ylabel('Theta (°)')
        self.ax_domain.set_title('Cost domain')
        self.ax_domain.legend(fontsize=8)
        self.canvas.draw()

    def _on_error(self, msg):
        messagebox.showerror("Error", msg)
        self.running = False
        self.run_btn.config(state=tk.NORMAL)
        self.result_var.set("Error — see message.")


if __name__ == '__main__':
    root = tk.Tk()
    app = InversionApp(root)
    root.mainloop()
