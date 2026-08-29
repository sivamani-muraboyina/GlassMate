import { useEffect, useMemo, useState } from 'react'
import ReactDOM from 'react-dom/client'
import {
  ArrowRight,
  BriefcaseBusiness,
  CalendarClock,
  CheckCircle2,
  CircleDashed,
  FileText,
  Gauge,
  GitBranchPlus,
  MapPin,
  Moon,
  ShieldCheck,
  Sparkles,
  SunMedium,
  Target,
  TrendingUp,
  UserRound,
  Zap,
} from 'lucide-react'
import './styles.css'

// Backend API URL: configurable via VITE_API_URL environment variable
// Defaults to localhost development address
const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

const navItems = ['Overview', 'Candidate', 'Jobs', 'Resumes', 'Applications']

const seedData = {
  candidate: {
    full_name: 'Ava Patel',
    email: 'ava.patel@example.com',
    current_focus: 'ML platform engineer',
    location: 'Remote · US / EU',
    skills: ['Python', 'FastAPI', 'SQLAlchemy', 'React', 'LLM Systems', 'PostgreSQL'],
    experience: '5 years in AI product development',
  },
  jobs: [
    {
      id: 101,
      title: 'Senior AI Engineer',
      company: 'Northstar Labs',
      location: 'New York, NY',
      source: 'LinkedIn',
      score: 88,
      category: 'STRONG_MATCH',
      salary: '$180k - $220k',
      requirements: [
        'Python and backend systems',
        'LLM/NLP product experience',
        'FastAPI or equivalent API experience',
      ],
      status: 'Ready to apply',
    },
    {
      id: 102,
      title: 'Staff Product Engineer',
      company: 'SignalForge',
      location: 'Remote',
      source: 'Greenhouse',
      score: 73,
      category: 'NEAR_MATCH',
      salary: '$170k - $200k',
      requirements: [
        'Product-driven engineering',
        'Data platform experience',
        'Hands-on leadership',
      ],
      status: 'Resume review',
    },
    {
      id: 103,
      title: 'Applied ML Engineer',
      company: 'VectorIQ',
      location: 'Boston, MA',
      source: 'Wellfound',
      score: 58,
      category: 'POOR_MATCH',
      salary: '$150k - $185k',
      requirements: ['ML deployment', 'MLOps', 'Experiment tracking'],
      status: 'Keep monitoring',
    },
  ],
  resume: {
    name: 'AI Product Engineer - Approved',
    version: 'v5',
    readiness: 'Strong fit',
    last_updated: 'Today',
    highlight: 'Best fit for product, SDK, and backend systems work',
  },
  applications: [
    {
      id: 1,
      title: 'Northstar Labs',
      status: 'Application package ready',
      checklist: ['JD snapshot captured', 'Resume match confirmed', 'Critic passed'],
    },
    {
      id: 2,
      title: 'SignalForge',
      status: 'Awaiting approval',
      checklist: ['Resume proposal prepared', 'Follow-up reminder queued'],
    },
  ],
}

function formatStatus(score) {
  if (score >= 80) return 'STRONG_MATCH'
  if (score >= 60) return 'NEAR_MATCH'
  return 'POOR_MATCH'
}

function App() {
  const [dark, setDark] = useState(true)
  const [activeNav, setActiveNav] = useState('Overview')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [data, setData] = useState(seedData)

  useEffect(() => {
    let cancelled = false

    async function loadData() {
      setLoading(true)
      setError('')

      try {
        const response = await fetch(`${API_URL}/health`)
        if (!response.ok) {
          throw new Error('Backend unavailable')
        }

        const candidateResponse = await fetch(`${API_URL}/candidates/1`)
        const candidateData = candidateResponse.ok ? await candidateResponse.json() : null

        const fallback = {
          ...seedData,
          candidate: candidateData
            ? {
                full_name: candidateData.full_name,
                email: candidateData.email,
                current_focus: 'Career signal matched to current opportunities',
                location: 'Remote · US / EU',
                skills: candidateData.skills?.map((skill) => skill.name) ?? seedData.candidate.skills,
                experience: candidateData.experiences?.[0]
                  ? `${candidateData.experiences[0].title} at ${candidateData.experiences[0].employer}`
                  : seedData.candidate.experience,
              }
            : seedData.candidate,
        }

        if (!cancelled) {
          setData(fallback)
        }
      } catch (fetchError) {
        if (!cancelled) {
          setData(seedData)
          setError('Live backend is unavailable; showing the current GlassMate workspace snapshot.')
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    loadData()
    return () => {
      cancelled = true
    }
  }, [])

  const summaryCards = useMemo(
    () => [
      {
        label: 'Candidate readiness',
        value: '92%',
        detail: 'Strong fit across required skills',
        tone: 'cyan',
        icon: <Gauge size={18} />,
      },
      {
        label: 'Active jobs',
        value: String(data.jobs.length),
        detail: 'Across inbound and outbound sources',
        tone: 'purple',
        icon: <BriefcaseBusiness size={18} />,
      },
      {
        label: 'Resume status',
        value: data.resume.version,
        detail: data.resume.readiness,
        tone: 'green',
        icon: <FileText size={18} />,
      },
      {
        label: 'Applications',
        value: String(data.applications.length),
        detail: 'Prepared and tracking follow-ups',
        tone: 'amber',
        icon: <CalendarClock size={18} />,
      },
    ],
    [data],
  )

  const primaryJob = data.jobs[0]

  return (
    <div className={`page-shell ${dark ? 'theme-dark' : 'theme-light'}`}>
      <header className="topbar">
        <div className="brand-wrap">
          <div className="brand-mark">
            <span className="brand-block" />
          </div>
          <div className="brand-copy">
            <span className="brand-name">GlassMate</span>
            <span className="brand-tag">Career intelligence</span>
          </div>
        </div>

        <nav className="main-nav" aria-label="Main navigation">
          {navItems.map((item) => (
            <button
              key={item}
              type="button"
              className={`nav-link ${item === activeNav ? 'active' : ''}`}
              onClick={() => setActiveNav(item)}
            >
              {item}
            </button>
          ))}
        </nav>

        <div className="header-actions">
          <button className="theme-toggle" type="button" onClick={() => setDark((value) => !value)}>
            {dark ? <SunMedium size={16} /> : <Moon size={16} />}
            <span>{dark ? 'Light' : 'Dark'}</span>
          </button>
        </div>
      </header>

      <main className="app-shell">
        <section className="hero-panel">
          <div className="hero-copy">
            <div className="pill">
              <span className="pill-dot" />
              GlassMate workflow
            </div>
            <h1>
              Move from<a href="#"> job discovery</a>
              <span>to confident application</span>
            </h1>
            <p>
              Evaluate candidates against job requirements, prepare evidence-backed resume proposals,
              validate application materials, and track follow-ups without losing context.
            </p>
            <div className="cta-row">
              <button className="primary-btn" type="button">
                Review opportunities
              </button>
              <button className="secondary-btn" type="button">
                Open resume strategy
              </button>
            </div>
          </div>

          <div className="hero-card">
            <div className="hero-card-head">
              <div className="status-badge success">
                <CheckCircle2 size={14} />
                Active pipeline
              </div>
              <span className="mini-meta">Updated today</span>
            </div>

            <div className="hero-metric-grid">
              <div className="metric-tile">
                <span className="metric-label">Fit score</span>
                <strong>{primaryJob.score}%</strong>
                <small>{formatStatus(primaryJob.score)}</small>
              </div>
              <div className="metric-tile accent">
                <span className="metric-label">Resume</span>
                <strong>{data.resume.version}</strong>
                <small>{data.resume.readiness}</small>
              </div>
            </div>

            <div className="hero-list">
              <div className="list-row">
                <span className="row-icon green"><ShieldCheck size={14} /></span>
                <div>
                  <strong>Critic validation</strong>
                  <small>Application package reviewed and approved</small>
                </div>
              </div>
              <div className="list-row">
                <span className="row-icon blue"><GitBranchPlus size={14} /></span>
                <div>
                  <strong>Resume proposal</strong>
                  <small>{data.resume.highlight}</small>
                </div>
              </div>
              <div className="list-row">
                <span className="row-icon violet"><Target size={14} /></span>
                <div>
                  <strong>Opportunity priority</strong>
                  <small>{primaryJob.company} · {primaryJob.title}</small>
                </div>
              </div>
            </div>
          </div>
        </section>

        {error ? <div className="system-banner">{error}</div> : null}

        <section className="summary-grid">
          {summaryCards.map((card) => (
            <article key={card.label} className={`summary-card tone-${card.tone}`}>
              <div className="summary-topline">
                <span className="summary-icon">{card.icon}</span>
                <span className="summary-label">{card.label}</span>
              </div>
              <strong>{card.value}</strong>
              <small>{card.detail}</small>
            </article>
          ))}
        </section>

        <section className="workspace-grid">
          <div className="panel-column">
            <article className="panel-card">
              <div className="panel-header">
                <div>
                  <span className="eyebrow">Candidate</span>
                  <h2>{data.candidate.full_name}</h2>
                </div>
                <button type="button" className="ghost-btn">
                  <UserRound size={16} />
                  Profile
                </button>
              </div>

              <div className="profile-line">
                <span><MapPin size={14} /> {data.candidate.location}</span>
                <span><Sparkles size={14} /> {data.candidate.current_focus}</span>
              </div>

              <div className="skills-wrap">
                {data.candidate.skills.map((skill) => (
                  <span key={skill} className="skill-pill">{skill}</span>
                ))}
              </div>

              <div className="info-block">
                <h3>Experience</h3>
                <p>{data.candidate.experience}</p>
              </div>
            </article>

            <article className="panel-card">
              <div className="panel-header small-gap">
                <div>
                  <span className="eyebrow">Resume strategy</span>
                  <h3>{data.resume.name}</h3>
                </div>
                <span className="chip success">{data.resume.readiness}</span>
              </div>

              <p className="muted-copy">{data.resume.highlight}</p>
              <div className="resume-meta">
                <span>Version {data.resume.version}</span>
                <span>Updated {data.resume.last_updated}</span>
              </div>
            </article>
          </div>

          <div className="panel-column large">
            <article className="panel-card">
              <div className="panel-header">
                <div>
                  <span className="eyebrow">Priority opportunities</span>
                  <h2>Job matches</h2>
                </div>
                <button type="button" className="ghost-btn">
                  View all
                  <ArrowRight size={16} />
                </button>
              </div>

              {loading ? (
                <div className="state-block">
                  <CircleDashed size={18} className="spin" />
                  Loading GlassMate data…
                </div>
              ) : data.jobs.length === 0 ? (
                <div className="state-block empty">
                  No active opportunities match the current candidate profile.
                </div>
              ) : (
                <div className="job-list">
                  {data.jobs.map((job) => (
                    <div key={job.id} className="job-row">
                      <div className="job-main">
                        <div className="job-headline">
                          <div>
                            <strong>{job.title}</strong>
                            <span>{job.company}</span>
                          </div>
                          <span className={`score-chip ${job.category.toLowerCase()}`}>
                            {job.score}%
                          </span>
                        </div>
                        <div className="job-meta-line">
                          <span><MapPin size={14} /> {job.location}</span>
                          <span>{job.source}</span>
                          <span>{job.salary}</span>
                        </div>
                        <ul className="job-bullets">
                          {job.requirements.map((requirement) => (
                            <li key={requirement}>{requirement}</li>
                          ))}
                        </ul>
                      </div>
                      <div className="job-aside">
                        <span className="job-status">{job.status}</span>
                        <span className="job-tag">{job.category}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </article>
          </div>
        </section>

        <section className="bottom-grid">
          <article className="panel-card">
            <div className="panel-header small-gap">
              <div>
                <span className="eyebrow">Application pipeline</span>
                <h3>Prepared materials</h3>
              </div>
              <span className="chip info">{data.applications.length} tracked</span>
            </div>

            <div className="application-list">
              {data.applications.map((application) => (
                <div key={application.id} className="application-item">
                  <div>
                    <strong>{application.title}</strong>
                    <span>{application.status}</span>
                  </div>
                  <ul>
                    {application.checklist.map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </article>

          <article className="panel-card">
            <div className="panel-header small-gap">
              <div>
                <span className="eyebrow">Signals</span>
                <h3>Workflow highlights</h3>
              </div>
              <TrendingUp size={18} className="signal-icon" />
            </div>

            <div className="signal-stack">
              <div className="signal-line">
                <span>JD analysis</span>
                <strong>Complete</strong>
              </div>
              <div className="signal-line">
                <span>Requirement match</span>
                <strong>Verified</strong>
              </div>
              <div className="signal-line">
                <span>Critic review</span>
                <strong>PASS</strong>
              </div>
              <div className="signal-line">
                <span>Follow-up cadence</span>
                <strong>On track</strong>
              </div>
            </div>
          </article>
        </section>
      </main>
    </div>
  )
}

export default App

ReactDOM.createRoot(document.getElementById('root')).render(<App />)
