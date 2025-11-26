(function(){
	const hasToken = !!localStorage.getItem('access');
	const login = document.getElementById('nav-login');
	const register = document.getElementById('nav-register');
	const logoutBtn = document.getElementById('nav-logout');
	const adminQuickBtn = document.getElementById('admin-quick-link');
	if (adminQuickBtn) {
		adminQuickBtn.addEventListener('click', () => { window.location.href = '/admin-panel/'; });
	}
	function toggleAdminQuickBtn(){
		if (!adminQuickBtn) return;
		const isAdmin = hasToken && localStorage.getItem('userRole') === 'admin';
		adminQuickBtn.classList.toggle('hidden', !isAdmin);
	}
	if (login) login.style.display = hasToken ? 'none' : 'inline-flex';
	if (register) register.style.display = hasToken ? 'none' : 'inline-flex';
	if (logoutBtn) logoutBtn.style.display = hasToken ? 'inline-flex' : 'none';
	toggleAdminQuickBtn();
	if (logoutBtn) logoutBtn.addEventListener('click', () => {
		localStorage.removeItem('access');
		localStorage.removeItem('refresh');
		localStorage.removeItem('userRole');
		window.location.href = '/';
	});
	// theme toggle
	const themeToggle = document.getElementById('theme-toggle');
	const root = document.documentElement;
	const saved = localStorage.getItem('theme');
	if (saved === 'dark') root.classList.add('dark');
	if (themeToggle) themeToggle.addEventListener('click', () => {
		root.classList.toggle('dark');
		localStorage.setItem('theme', root.classList.contains('dark') ? 'dark' : 'light');
	});

	// Toast helper
	function showToast(message, type='info'){
		const root = document.getElementById('toast-root');
		if (!root) return alert(message);
		const el = document.createElement('div');
		const color = type==='error' ? 'bg-red-600' : type==='success' ? 'bg-green-600' : 'bg-gray-800';
		el.className = `text-white px-4 py-2 rounded shadow ${color}`;
		el.textContent = message;
		root.appendChild(el);
		setTimeout(()=>{ el.remove(); }, 2600);
	}
	window.showToast = showToast;

    // global API helper with optional silent 401
    window.libmApi = async function(path, options={}){
		const token = localStorage.getItem('access');
		const headers = Object.assign({'Content-Type': 'application/json'}, options.headers||{});
		if (token) headers['Authorization'] = 'Bearer ' + token;
		const res = await fetch(path, { ...options, headers });
		if (res.status === 401) {
            if (!options.silent401) {
                showToast('Bu işlem için giriş yapmanız gerekiyor.', 'error');
            }
			// try refresh if refresh exists
			if (localStorage.getItem('refresh')){
				const r = await fetch('/api/auth/token/refresh/', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ refresh: localStorage.getItem('refresh') }) });
				if (r.ok){ const data = await r.json(); localStorage.setItem('access', data.access); return window.libmApi(path, options); }
			}
		}
		return res;
	}

	async function refreshUserRole(){
		if(!hasToken) return;
		try{
			const res = await window.libmApi('/api/users/me/', { silent401: true });
			if(res.ok){
				const data = await res.json();
				localStorage.setItem('userRole', data.is_staff ? 'admin' : 'user');
			}else{
				localStorage.removeItem('userRole');
			}
		}catch(err){
			localStorage.removeItem('userRole');
		}
		toggleAdminQuickBtn();
	}

	if(hasToken){
		refreshUserRole();
	}
})();
