import React, { useEffect, useState } from 'react'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

function TechBadge({ name }) {
  return <span className="tech-badge">{name}</span>
}

function ProjectCard({ p }) {
  return (
    <article className="card">
      <div className="card-body">
        <h3 className="card-title">{p.title}</h3>
        <p className="card-desc">{p.description}</p>
        {p.technologies && p.technologies.length > 0 && (
          <div className="card-techs">
            {p.technologies.map((t, i) => <TechBadge key={i} name={t} />)}
          </div>
        )}
      </div>
      <div className="card-footer">
        {p.link ? <a className="card-link" href={p.link} target="_blank" rel="noreferrer">Voir</a> : <span className="muted">Pas de lien</span>}
        <small className="muted">{p.created_at ? new Date(p.created_at).toLocaleDateString() : ''}</small>
      </div>
    </article>
  )
}

export default function App() {
  const [projects, setProjects] = useState([])
  const [techs, setTechs] = useState([])
  const [certs, setCerts] = useState([])
  const [contact, setContact] = useState({ name: '', email: '', message: '' })
  const [msg, setMsg] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [sending, setSending] = useState(false)

  async function loadData() {
    setLoading(true)
    setError(null)
    try {
      const [pRes, tRes, cRes] = await Promise.all([
        fetch(`${API_BASE}/projects/`),
        fetch(`${API_BASE}/technologies/`),
        fetch(`${API_BASE}/certifications/`),
      ])

      if (!pRes.ok) {
        const txt = await pRes.text()
        throw new Error(`/projects/ failed: ${pRes.status} ${txt}`)
      }
      if (!tRes.ok) {
        const txt = await tRes.text()
        throw new Error(`/technologies/ failed: ${tRes.status} ${txt}`)
      }
      if (!cRes.ok) {
        const txt = await cRes.text()
        throw new Error(`/certifications/ failed: ${cRes.status} ${txt}`)
      }

      const pJson = await pRes.json()
      const tJson = await tRes.json()
      const cJson = await cRes.json()
      setProjects(pJson || [])
      setTechs(tJson || [])
      setCerts(cJson || [])
    } catch (err) {
      console.error(err)
      setError(String(err))
      setProjects([])
      setTechs([])
      setCerts([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { loadData() }, [])

  function validateContact() {
    if (!contact.name.trim()) return 'Nom requis'
    if (!contact.email.includes('@')) return 'Email invalide'
    if (!contact.message.trim()) return 'Message requis'
    return null
  }

  async function submitContact(e) {
    e.preventDefault()
    const v = validateContact()
    if (v) { setMsg(v); return }
    setSending(true)
    setMsg('Envoi...')
    try {
      const res = await fetch(`${API_BASE}/contact/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(contact)
      })
      if (!res.ok) throw new Error('Erreur')
      setMsg('Message envoyé — merci !')
      setContact({ name: '', email: '', message: '' })
    } catch (err) {
      console.error(err)
      setMsg('Erreur lors de l\'envoi')
    } finally {
      setSending(false)
    }
  }

  return (
    <div className="app">
      <header className="header">
        <div className="header-inner">
          <h1>Team‑Z — Portfolio (Demo)</h1>
          <div className="actions">
            <button onClick={loadData} className="btn">Rafraîchir</button>
          </div>
        </div>
      </header>

      <main className="container">
        {loading && <div className="center">Chargement...</div>}
        {error && <div className="error">{error}</div>}

        <section>
          <h2>Projets</h2>
          <div className="grid">
            {projects.map(p => <ProjectCard key={p.id || p._id || p.title} p={p} />)}
          </div>
          {!loading && projects.length === 0 && <div className="muted">Aucun projet trouvé.</div>}
        </section>

        <aside className="sidebar">
          <section>
            <h2>Technologies</h2>
            <ul className="tech-list">
              {techs.map(t => (
                <li key={t.id || t.name} className="tech-item">
                  <strong>{t.name}</strong>
                  {t.description ? <div className="muted small">{t.description}</div> : null}
                  {t.level ? <span className="tech-level">{t.level}</span> : null}
                </li>
              ))}
              {!loading && techs.length === 0 && <li className="muted">Aucune technologie trouvée.</li>}
            </ul>
          </section>

          <section>
            <h2>Certifications</h2>
            <ul className="cert-list">
              {certs.map(c => (
                <li key={c.id || c.title} className="cert-item">
                  <div className="cert-title">{c.title}</div>
                  <div className="muted small">{c.issuer} — {c.date}</div>
                  {c.technologies && c.technologies.length > 0 && (
                    <div className="cert-techs">
                      {c.technologies.map((t, i) => <TechBadge key={i} name={t} />)}
                    </div>
                  )}
                </li>
              ))}
              {!loading && certs.length === 0 && <li className="muted">Aucune certification trouvée.</li>}
            </ul>
          </section>

          <section>
            <h2>Contact</h2>
            <form onSubmit={submitContact} className="contact-form">
              <input placeholder="Nom" value={contact.name} onChange={e => setContact({...contact, name: e.target.value})} />
              <input placeholder="Email" value={contact.email} onChange={e => setContact({...contact, email: e.target.value})} />
              <textarea placeholder="Message" value={contact.message} onChange={e => setContact({...contact, message: e.target.value})} />
              <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                <button type="submit" className="btn" disabled={sending}>{sending ? 'Envoi...' : 'Envoyer'}</button>
                <div className="msg">{msg}</div>
              </div>
            </form>
          </section>
        </aside>

      </main>

      <footer className="footer">Démo — données de test</footer>
    </div>
  )
}
