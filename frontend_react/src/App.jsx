import { useEffect, useMemo, useState } from 'react'
import './App.css'

const DEFAULT_API = import.meta.env.VITE_API_BASE_URL || '/api'

async function fetchJson(baseUrl, path) {
  const response = await fetch(`${baseUrl.replace(/\/$/, '')}${path}`)
  if (!response.ok) {
    throw new Error(`${response.status} ${response.statusText}`)
  }
  return response.json()
}

function chunkItems(items, size) {
  const chunks = []
  for (let i = 0; i < items.length; i += size) {
    chunks.push(items.slice(i, i + size))
  }
  return chunks
}

function App() {
  const [apiUrl, setApiUrl] = useState(DEFAULT_API)
  const [apiInput, setApiInput] = useState(DEFAULT_API)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [health, setHealth] = useState(null)
  const [portfolio, setPortfolio] = useState(null)
  const [projects, setProjects] = useState([])
  const [experiences, setExperiences] = useState([])
  const [skills, setSkills] = useState([])
  const [technologies, setTechnologies] = useState([])
  const [hobbies, setHobbies] = useState([])
  const [relatedProjects, setRelatedProjects] = useState([])
  const [selectedSkill, setSelectedSkill] = useState('')

  const [spreadIndex, setSpreadIndex] = useState(0)
  const [turning, setTurning] = useState(null)
  const [soundEnabled, setSoundEnabled] = useState(true)

  const person = portfolio?.infos_personnels?.[0] ?? {}
  const education = portfolio?.parcours_scolaire ?? []

  const projectPairs = useMemo(() => {
    const cards = projects.map((project) => ({
      title: project.nom,
      subtitle: `${project.entreprise ?? 'Entreprise n/a'} · ${project.status ?? 'n/a'}`,
      body: project.description ?? 'Aucune description disponible.',
      footer: `${project.date_debut ?? 'n/a'} → ${project.date_fin ?? 'n/a'}`,
      link: project.lien_github ?? null,
    }))
    return chunkItems(cards, 4)
  }, [projects])

  const experiencePairs = useMemo(() => {
    const cards = experiences.map((exp) => ({
      title: exp.nom,
      subtitle: `${exp.company ?? 'Entreprise n/a'} · ${exp.role ?? 'Role n/a'}`,
      body: exp.description ?? 'Aucune description disponible.',
      footer: `${exp.date_debut ?? 'n/a'} → ${exp.date_fin ?? 'n/a'}`,
    }))
    return chunkItems(cards, 4)
  }, [experiences])

  const spreads = useMemo(() => {
    const base = [
      {
        left: 'cover-left',
        right: 'cover-right',
      },
      {
        left: 'summary-left',
        right: 'summary-right',
      },
    ]

    projectPairs.forEach((_, index) => {
      base.push({
        left: `projects-left-${index}`,
        right: `projects-right-${index}`,
      })
    })

    experiencePairs.forEach((_, index) => {
      base.push({
        left: `experiences-left-${index}`,
        right: `experiences-right-${index}`,
      })
    })

    base.push(
      {
        left: 'graph-left',
        right: 'graph-right',
      },
      {
        left: 'contact-left',
        right: 'contact-right',
      },
    )

    return base
  }, [experiencePairs, projectPairs])

  async function loadData(baseUrl) {
    setLoading(true)
    setError('')

    try {
      const [healthData, globalData, projectsData, experiencesData, skillsData, technologiesData, hobbiesData] =
        await Promise.all([
          fetchJson(baseUrl, '/health'),
          fetchJson(baseUrl, '/profile/global'),
          fetchJson(baseUrl, '/projects'),
          fetchJson(baseUrl, '/experiences'),
          fetchJson(baseUrl, '/skills'),
          fetchJson(baseUrl, '/technologies'),
          fetchJson(baseUrl, '/profile/hobbies'),
        ])

      setHealth(healthData)
      setPortfolio(globalData)
      setProjects(projectsData)
      setExperiences(experiencesData)
      setSkills(skillsData)
      setTechnologies(technologiesData)
      setHobbies(hobbiesData)
      setSpreadIndex(0)

      const firstSkill = skillsData?.[0]?.nom ?? ''
      setSelectedSkill(firstSkill)
      if (firstSkill) {
        const related = await fetchJson(baseUrl, `/skills/${encodeURIComponent(firstSkill)}/projects`)
        setRelatedProjects(related)
      } else {
        setRelatedProjects([])
      }
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : 'Erreur inconnue')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData(apiUrl)
  }, [apiUrl])

  useEffect(() => {
    if (!selectedSkill) {
      setRelatedProjects([])
      return
    }

    let cancelled = false
    fetchJson(apiUrl, `/skills/${encodeURIComponent(selectedSkill)}/projects`)
      .then((data) => {
        if (!cancelled) {
          setRelatedProjects(data)
        }
      })
      .catch(() => {
        if (!cancelled) {
          setRelatedProjects([])
        }
      })

    return () => {
      cancelled = true
    }
  }, [apiUrl, selectedSkill])

  function playFlipSound() {
    if (!soundEnabled || typeof window === 'undefined') {
      return
    }
    try {
      const context = new window.AudioContext()
      const duration = 0.15
      const buffer = context.createBuffer(1, context.sampleRate * duration, context.sampleRate)
      const data = buffer.getChannelData(0)
      for (let i = 0; i < data.length; i += 1) {
        const envelope = 1 - i / data.length
        data[i] = (Math.random() * 2 - 1) * envelope * 0.3
      }
      const source = context.createBufferSource()
      source.buffer = buffer
      const gainNode = context.createGain()
      gainNode.gain.value = 0.2
      source.connect(gainNode)
      gainNode.connect(context.destination)
      source.start()
      source.stop(context.currentTime + duration)
    } catch {
      // ignore audio failures
    }
  }

  function turnPage(direction) {
    if (turning) {
      return
    }
    const isNext = direction === 'next'
    const target = isNext ? spreadIndex + 1 : spreadIndex - 1
    if (target < 0 || target >= spreads.length) {
      return
    }

    setTurning(direction)
    playFlipSound()
    window.setTimeout(() => {
      setSpreadIndex(target)
      setTurning(null)
    }, 240)
  }

  function onBookClick(event) {
    const interactive = event.target.closest('button, a, input, select, option, label')
    if (interactive) {
      return
    }

    const rect = event.currentTarget.getBoundingClientRect()
    const x = event.clientX - rect.left
    const middle = rect.width / 2

    if (x >= middle) {
      turnPage('next')
    } else {
      turnPage('prev')
    }
  }

  function goToSpread(index) {
    if (index < 0 || index >= spreads.length) {
      return
    }
    setSpreadIndex(index)
  }

  useEffect(() => {
    function onKeyDown(event) {
      if (event.key === 'ArrowRight') {
        turnPage('next')
      }
      if (event.key === 'ArrowLeft') {
        turnPage('prev')
      }
    }

    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  })

  function renderCard(item) {
    return (
      <article className="book-card" key={`${item.title}-${item.footer}`}>
        <h4>{item.title}</h4>
        <p className="small-muted">{item.subtitle}</p>
        <p>{item.body}</p>
        <p className="small-muted">{item.footer}</p>
        {item.link && (
          <a href={item.link} target="_blank" rel="noreferrer">
            Ouvrir GitHub
          </a>
        )}
      </article>
    )
  }

  function renderPage(pageKey) {
    if (pageKey === 'cover-left') {
      return (
        <div className="leaf cover-page">
          <h1>Le Livre</h1>
          <h1>du Portfolio</h1>
          <h2>{`${person.prenom ?? ''} ${person.nom ?? ''}`.trim() || 'Portfolio'}</h2>
          <p>
            Journal interactif des projets, expériences et compétences alimenté par FastAPI, MongoDB
            et Neo4j.
          </p>
          <p className="small-muted action-hint">Clique à droite pour ouvrir.</p>
        </div>
      )
    }

    if (pageKey === 'cover-right') {
      return (
        <div className="leaf intro-page">
          <h2>Édition Data-Driven</h2>
          <p>Ce livre présente une lecture en double-page réaliste.</p>
          <ul>
            <li>MongoDB pour les documents</li>
            <li>Neo4j pour les relations</li>
            <li>React pour l’expérience interactive</li>
          </ul>
          <p className="small-muted">
            API: {health ? `connectée (v${health.version ?? 'n/a'})` : 'non disponible'}
          </p>
        </div>
      )
    }

    if (pageKey === 'summary-left') {
      return (
        <div className="leaf">
          <h2>Sommaire</h2>
          <ol className="toc-list">
            <li>
              <button type="button" onClick={() => goToSpread(2)}>
                Projets
              </button>
            </li>
            <li>
              <button type="button" onClick={() => goToSpread(2 + projectPairs.length)}>
                Expériences
              </button>
            </li>
            <li>
              <button type="button" onClick={() => goToSpread(2 + projectPairs.length + experiencePairs.length)}>
                Graph compétences
              </button>
            </li>
            <li>
              <button
                type="button"
                onClick={() => goToSpread(2 + projectPairs.length + experiencePairs.length + 1)}
              >
                Contact
              </button>
            </li>
          </ol>
        </div>
      )
    }

    if (pageKey === 'summary-right') {
      return (
        <div className="leaf">
          <h2>Profil</h2>
          <p>{person.description ?? 'Description indisponible.'}</p>
          <ul>
            <li>Projets: {projects.length}</li>
            <li>Expériences: {experiences.length}</li>
            <li>Skills: {skills.length}</li>
            <li>Technologies: {technologies.length}</li>
          </ul>
          <p className="small-muted action-hint">Clique à droite/gauche sur le livre pour tourner.</p>
        </div>
      )
    }

    if (pageKey.startsWith('projects-')) {
      const pageIndex = Number(pageKey.split('-').at(-1) ?? 0)
      const chunk = projectPairs[pageIndex] ?? []
      return (
        <div className="leaf">
          <h2>Projets · Page {pageIndex + 1}</h2>
          <div className="card-grid">{chunk.map((item) => renderCard(item))}</div>
        </div>
      )
    }

    if (pageKey.startsWith('experiences-')) {
      const pageIndex = Number(pageKey.split('-').at(-1) ?? 0)
      const chunk = experiencePairs[pageIndex] ?? []
      return (
        <div className="leaf">
          <h2>Expériences · Page {pageIndex + 1}</h2>
          <div className="card-grid">{chunk.map((item) => renderCard(item))}</div>
        </div>
      )
    }

    if (pageKey === 'graph-left') {
      return (
        <div className="leaf">
          <h2>Graph Intelligent</h2>
          <label htmlFor="skill-select">Compétence à explorer</label>
          <select
            id="skill-select"
            value={selectedSkill}
            onChange={(event) => setSelectedSkill(event.target.value)}
          >
            {skills.map((skill) => (
              <option key={skill.id ?? skill.nom} value={skill.nom}>
                {skill.nom}
              </option>
            ))}
          </select>

          <h3>Technologies</h3>
          <div className="chips-wrap">
            {technologies.map((tech) => (
              <span className="chip" key={tech.id ?? tech.nom}>
                {tech.nom}
              </span>
            ))}
          </div>
        </div>
      )
    }

    if (pageKey === 'graph-right') {
      return (
        <div className="leaf">
          <h2>Projets liés à {selectedSkill || '...'}</h2>
          {relatedProjects.length === 0 ? (
            <p className="small-muted">Aucun projet lié trouvé pour cette compétence.</p>
          ) : (
            <ul>
              {relatedProjects.map((project) => (
                <li key={project.id ?? project.nom}>
                  <strong>{project.nom}</strong> — {project.status ?? 'n/a'}
                </li>
              ))}
            </ul>
          )}
        </div>
      )
    }

    if (pageKey === 'contact-left') {
      return (
        <div className="leaf">
          <h2>Contact</h2>
          <ul>
            <li>Email: {person?.contact?.mail ?? 'n/a'}</li>
            <li>Téléphone: {person?.contact?.tel ?? 'n/a'}</li>
            <li>LinkedIn: {person?.contact?.linkedin ?? 'n/a'}</li>
          </ul>

          <h3>Parcours scolaire</h3>
          <ul>
            {education.map((item) => (
              <li key={item.id ?? item.school_name}>
                {item.school_name} · {item.degree} ({item.start_year} - {item.end_year})
              </li>
            ))}
          </ul>
        </div>
      )
    }

    return (
      <div className="leaf">
        <h2>Hobbies & Fin</h2>
        <ul>
          {hobbies.map((hobby) => (
            <li key={hobby.id ?? hobby.nom}>
              <strong>{hobby.nom}</strong> · {hobby.description}
            </li>
          ))}
        </ul>
        <p className="small-muted">Fin du livre. Clique à gauche pour revenir.</p>
      </div>
    )
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <h1>Portfolio React — Livre Interactif</h1>
        <div className="api-controls">
          <input
            value={apiInput}
            onChange={(event) => setApiInput(event.target.value)}
            placeholder="/api"
            aria-label="URL API"
          />
          <button type="button" onClick={() => setApiUrl(apiInput)}>
            Charger
          </button>
          <button type="button" onClick={() => setSoundEnabled((prev) => !prev)}>
            Son: {soundEnabled ? 'ON' : 'OFF'}
          </button>
        </div>
      </header>

      {loading && <p className="status">Chargement des pages...</p>}
      {error && <p className="status error">Erreur API: {error}</p>}

      {!loading && !error && (
        <>
          <section
            className={`book-scene ${turning ? `turn-${turning}` : ''}`}
            onClick={onBookClick}
            aria-label="Livre interactif"
            role="button"
            tabIndex={0}
          >
            <div className="book-shadow" />
            <div className="book-spread">
              <div className="book-page left">{renderPage(spreads[spreadIndex].left)}</div>
              <div className="spine" />
              <div className="book-page right">{renderPage(spreads[spreadIndex].right)}</div>
            </div>
            <div className="click-zones">
              <span>⬅️ Cliquer à gauche</span>
              <span>Cliquer à droite ➡️</span>
            </div>
          </section>

          <footer className="pager">
            <button type="button" onClick={() => turnPage('prev')} disabled={spreadIndex === 0}>
              Page précédente
            </button>
            <span>
              Spread {spreadIndex + 1} / {spreads.length}
            </span>
            <button
              type="button"
              onClick={() => turnPage('next')}
              disabled={spreadIndex >= spreads.length - 1}
            >
              Page suivante
            </button>
          </footer>
        </>
      )}
    </main>
  )
}

export default App
