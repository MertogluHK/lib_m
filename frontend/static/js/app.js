(function(){
	// Check if token exists and is potentially valid
	const token = localStorage.getItem('access');
	const hasToken = !!token;
	
	// If token exists but is clearly invalid (too short or malformed), clear it
	if (token && (token.length < 20 || !token.includes('.'))) {
		localStorage.removeItem('access');
		localStorage.removeItem('refresh');
		localStorage.removeItem('userRole');
	}
	
	const login = document.getElementById('nav-login');
	const register = document.getElementById('nav-register');
	const logoutBtn = document.getElementById('nav-logout');
	const profileLink = document.getElementById('nav-profile');
	const adminQuickBtn = document.getElementById('admin-quick-link');
	const libmLink = document.querySelector('a.brand-font');
	
	function handleLibMClick(e) {
		const isAdmin = localStorage.getItem('userRole') === 'admin';
		if (isAdmin) {
			e.preventDefault();
			window.location.href = '/admin-panel/';
		}
	}
	
	if (libmLink) {
		libmLink.addEventListener('click', handleLibMClick);
	}
	
	if (adminQuickBtn) {
		adminQuickBtn.style.display = 'none';
	}
	function toggleAdminQuickBtn(){
		if (!adminQuickBtn) return;
		const currentToken = localStorage.getItem('access');
		const isAdmin = currentToken && localStorage.getItem('userRole') === 'admin';
		adminQuickBtn.classList.toggle('hidden', !isAdmin);
	}
	
	function toggleProfileLink(){
		if (!profileLink) return;
		const isAdmin = localStorage.getItem('userRole') === 'admin';
		profileLink.style.display = (localStorage.getItem('access') && !isAdmin) ? 'inline-flex' : 'none';
	}
	
	function toggleAdminUI(){
		const isAdmin = localStorage.getItem('userRole') === 'admin';
		const navLinks = document.querySelectorAll('nav a');
		const footer = document.querySelector('footer');
		
		navLinks.forEach(link => {
			if (link.textContent.trim() === 'Ana Sayfa' || link.textContent.trim() === 'Kitaplar' || link.textContent.trim() === 'Topluluk') {
				link.style.display = isAdmin ? 'none' : '';
			}
		});
		
		if (footer) {
			footer.style.display = isAdmin ? 'none' : '';
		}
	}
	
	// ✅ DÜZELTME: Tekrar tanımlama kaldırıldı, sadece token değişkenini kullan
	if (login) login.style.display = token ? 'none' : 'inline-flex';
	if (register) register.style.display = token ? 'none' : 'inline-flex';
	if (logoutBtn) logoutBtn.style.display = token ? 'inline-flex' : 'none';
	toggleProfileLink();
	toggleAdminQuickBtn();
	toggleAdminUI();
	
	// Reserve CTA button logic
	const reserveCta = document.getElementById('reserveCta');
	const loginModal = document.getElementById('loginRequiredModal');
	const loginModalCancel = document.getElementById('loginModalCancel');
	const loginModalGo = document.getElementById('loginModalGo');
	
	if (reserveCta) {
		reserveCta.addEventListener('click', () => {
			if (token) {
				// Kullanıcı giriş yapmışsa, direkt olarak rezervasyon sayfasına git
				window.location.href = '/reservations/';
			} else {
				// Giriş yapılmamışsa modal göster
				loginModal.classList.remove('hidden');
			}
		});
	}
	
	if (loginModalCancel) {
		loginModalCancel.addEventListener('click', () => {
			loginModal.classList.add('hidden');
		});
	}
	
	if (loginModalGo) {
		loginModalGo.addEventListener('click', () => {
			window.location.href = '/login/';
		});
	}
	
	// Modal'ı kapat eğer dışına tıklanırsa
	if (loginModal) {
		loginModal.addEventListener('click', (e) => {
			if (e.target === loginModal) {
				loginModal.classList.add('hidden');
			}
		});
	}
	
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

	// General Modal helper
	function showModal(title, message, primaryBtnText = 'Tamam', primaryBtnCallback = null) {
		const modal = document.getElementById('generalModal');
		const titleEl = document.getElementById('modalTitle');
		const messageEl = document.getElementById('modalMessage');
		const btnContainer = document.getElementById('modalButtons');
		
		titleEl.textContent = title;
		messageEl.textContent = message;
		
		// Clear previous buttons
		btnContainer.innerHTML = '';
		
		// Add primary button
		const primaryBtn = document.createElement('button');
		primaryBtn.className = 'flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium transition';
		primaryBtn.textContent = primaryBtnText;
		primaryBtn.addEventListener('click', () => {
			modal.classList.add('hidden');
			if (primaryBtnCallback) primaryBtnCallback();
		});
		btnContainer.appendChild(primaryBtn);
		
		modal.classList.remove('hidden');
	}
	window.showModal = showModal;

	// Modal'ı kapat eğer dışına tıklanırsa
	const generalModal = document.getElementById('generalModal');
	if (generalModal) {
		generalModal.addEventListener('click', (e) => {
			if (e.target === generalModal) {
				generalModal.classList.add('hidden');
			}
		});
	}

    // global API helper with optional silent 401
	window.libmApi = async function(path, options={}){
		console.debug('libmApi request', path, options && options.skipToken, options && options.silent401);
		let token = localStorage.getItem('access');
		const headers = Object.assign({'Content-Type': 'application/json'}, options.headers||{});
		
		// Only add token if it exists and we're not explicitly skipping it
		if (token && !options.skipToken) {
			headers['Authorization'] = 'Bearer ' + token;
		}
		
		let res = await fetch(path, { ...options, headers });

		// If caller explicitly asked to skip token handling, return raw response
		if (options && options.skipToken) {
			return res;
		}
		
		// Check for token errors - if 401, it's definitely a token error
		// Also check response body for token error messages
		let isTokenError = res.status === 401;
		if (!isTokenError && token && res.status >= 400 && res.status < 500) {
			try {
				const clone = res.clone();
				const text = await clone.text();
				if (text.includes('token') && (text.includes('invalid') || text.includes('expired') || text.includes('not valid') || text.includes('Given token not valid'))) {
					isTokenError = true;
				}
			} catch (e) {
				// If clone fails, we'll treat 401 as token error
			}
		}
		
		if (isTokenError) {
			// Clear invalid token immediately
			if (token) {
				localStorage.removeItem('access');
			}
			
			// try refresh if refresh exists
			const refreshToken = localStorage.getItem('refresh');
			let refreshSucceeded = false;
			
			if (refreshToken){
				try {
					const r = await fetch('/api/auth/token/refresh/', { 
						method:'POST', 
						headers:{'Content-Type':'application/json'}, 
						body: JSON.stringify({ refresh: refreshToken }) 
					});
					if (r.ok){ 
						const data = await r.json(); 
						localStorage.setItem('access', data.access); 
						// Retry the original request with new token
						const newHeaders = Object.assign({'Content-Type': 'application/json'}, options.headers||{});
						newHeaders['Authorization'] = 'Bearer ' + data.access;
						res = await fetch(path, { ...options, headers: newHeaders });
						refreshSucceeded = true;
					} else {
						// Refresh failed, clear all tokens
						localStorage.removeItem('refresh');
						localStorage.removeItem('userRole');
					}
				} catch (err) {
					// Refresh request failed, clear all tokens
					localStorage.removeItem('refresh');
					localStorage.removeItem('userRole');
				}
			} else {
				// No refresh token, clear user role
				localStorage.removeItem('userRole');
			}
			
			// If refresh failed and silent401 is true, try without token (for public endpoints)
			if (!refreshSucceeded && options.silent401) {
				const publicHeaders = Object.assign({'Content-Type': 'application/json'}, options.headers||{});
				// Ensure no Authorization header
				delete publicHeaders['Authorization'];
				try {
					res = await fetch(path, { ...options, headers: publicHeaders });
				} catch (err) {
					// If fetch fails, return the original response
					console.error('Error retrying without token:', err);
				}
			}
			
			// If not silent, show error and redirect
			if (!options.silent401 && !refreshSucceeded) {
				showToast('Bu işlem için giriş yapmanız gerekiyor.', 'error');
				setTimeout(() => {
					window.location.href = '/login/';
				}, 1500);
			}
		}
		return res;
	}

	async function refreshUserRole(){
		const token = localStorage.getItem('access');
		if(!token) {
			localStorage.removeItem('userRole');
			toggleAdminQuickBtn();
			toggleProfileLink();
			toggleAdminUI();
			return;
		}
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
		toggleProfileLink();
		toggleAdminUI();
	}

	// ✅ DÜZELTME: Tekrar tanımlama kaldırıldı, sadece token değişkenini kullan
	if(token){
		refreshUserRole();
	}
	
	// Profil link'i güncelle (admin ise gizle)
	window.addEventListener('storage', () => {
		toggleProfileLink();
		toggleAdminUI();
	});
})();