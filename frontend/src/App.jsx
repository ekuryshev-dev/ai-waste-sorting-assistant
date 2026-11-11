import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { clearChat, getChat, getJson, sendChat, sendPhoto, wakeService } from './api.js'

const services = {
  assistant: { name: 'AI assistant', url: '/health/assistant' },
  classification: { name: 'Photo identification', url: '/health/classification' },
  analytics: { name: 'Statistics', url: '/health/analytics' },
}
const pageService = { chat: 'assistant', photo: 'classification', dashboard: 'analytics' }
const KEEP_AWAKE_MS = 10 * 60 * 1000

const categories = [
  { key: 'recyclable', label: 'Recyclable', color: '#24825c' },
  { key: 'compostable', label: 'Compostable', color: '#4389b5' },
  { key: 'landfill', label: 'Landfill', color: '#d48745' },
  { key: 'unknown', label: 'Unknown', color: '#858da1' },
]

function Icon({ name }) {
  const shapes = {
    camera: <><rect x="3" y="6" width="18" height="15" rx="2" /><circle cx="12" cy="13.5" r="3.5" /><path d="M8 6l1-2h6l1 2" /></>,
    chat: <><path d="M4 5h16v11H9l-5 4V5Z" /><path d="M8 9h8M8 12h5" /></>,
    chart: <><path d="M4 20V11M10 20V5M16 20v-9M22 20H2" /></>,
    arrow: <path d="M5 12h14m-6-6 6 6-6 6" />,
    back: <path d="m15 5-7 7 7 7M8 12h13" />,
    upload: <><path d="M12 16V3m-5 5 5-5 5 5M4 16v4h16v-4" /></>,
    refresh: <><path d="M20 12a8 8 0 1 1-2.3-5.7" /><path d="M20 4v6h-6" /></>,
    send: <><path d="m3 11 18-8-8 18-2.5-7.5L3 11Z" /><path d="M10.5 13.5 21 3" /></>,
    check: <path d="m4 12 5 5L20 6" />,
    warning: <><path d="M12 3 2 21h20L12 3Z" /><path d="M12 9v5m0 3h.01" /></>,
    trash: <><path d="M4 7h16M10 11v6M14 11v6" /><path d="M6 7l1 13h10l1-13M9 7V4h6v3" /></>,
  }
  return <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{shapes[name]}</svg>
}

function Header({ page, goHome }) {
    return <header className="site-header">
      <div className="header-inner">
        <button className="brand" onClick={goHome} aria-label="Diligen home"><img src="/diligen-logo.png"
                                                                                  alt="Diligen"/></button>
        {page !== 'home' && <button className="back-link" onClick={goHome}><Icon name="back"/> Main menu</button>}
      </div>
    </header>
  }

  function ServiceLabel({status}) {
    if (status.state === 'waking') return <span className="service-label">Starting…</span>
    if (status.state === 'down') return <span className="service-label down">Not responding</span>
    return null
  }

  function Home({setPage, status}) {
    const cards = [
      {
        page: 'chat',
        icon: 'chat',
        title: 'Ask the AI assistant',
        text: 'Get answers to your questions about waste sorting and recycling.'
      },
      {
        page: 'photo',
        icon: 'camera',
        title: 'Identify an item',
        text: 'Upload a photo and find disposal instructions for your region.'
      },
      {
        page: 'dashboard',
        icon: 'chart',
        title: 'Explore statistics',
        text: 'See how classified waste is distributed across categories and time.'
      },
    ]
    return <main className="home-page">
      <section className="hero">
        <div>
          <span className="eyebrow">DILIGEN</span>
          <h1>How can we help?</h1>
          <p>Choose one of the three tools below.</p>
        </div>
        <div className="hero-mark" aria-hidden="true">♻</div>
      </section>
      <section className="home-actions" aria-label="Choose what you want to do">{cards.map(card =>
          <button key={card.page} className="action-card" onClick={() => setPage(card.page)}>
            <span className="card-top"><span className="card-icon"><Icon name={card.icon}/></span></span>
            <span className="card-title">{card.title} <ServiceLabel
                status={status[pageService[card.page]]}/></span><span className="card-text">{card.text}</span>
          </button>)}</section>
    </main>
  }

  function RegionSelect({regions, value, onChange, label = 'Region', showPlaceholder = true}) {
    return <label className="field-label">{label}<select value={value} onChange={event => onChange(event.target.value)}
                                                         disabled={!regions.length}>
      {showPlaceholder && <option value="">{regions.length ? 'Select a region' : 'No regions available'}</option>}
      {regions.map(region => <option key={region}
                                     value={region}>{region === '__all__' ? 'All regions' : region}</option>)}
    </select></label>
  }

  function useRegions(url) {
    const [regions, setRegions] = useState([])
    const [error, setError] = useState('')
    useEffect(() => {
      let active = true
      getJson(url).then(data => {
        if (active) setRegions(data.regions || [])
      })
          .catch(err => {
            if (active) setError(err.message)
          })
      return () => {
        active = false
      }
    }, [url])
    return {regions, error}
  }

  function PhotoPage() {
    const {regions, error: regionError} = useRegions('/classification/regions')
    const [region, setRegion] = useState('')
    const selectedRegion = regions.includes(region) ? region : ''
    const [file, setFile] = useState(null)
    const preview = useMemo(() => file ? URL.createObjectURL(file) : '', [file])
    const [dragging, setDragging] = useState(false)
    const [result, setResult] = useState(null)
    const [error, setError] = useState('')
    const [busy, setBusy] = useState(false)
    const fileInput = useRef(null)

    useEffect(() => () => {
      if (preview) URL.revokeObjectURL(preview)
    }, [preview])

    function chooseRegion(value) {
      setRegion(value)
      if (value && file) setError('')
    }

    function chooseFile(nextFile) {
      if (!nextFile) {
        setError('No image was received. Use Choose file to select one.');
        return
      }
      if (!['image/jpeg', 'image/png', 'image/webp'].includes(nextFile.type)) {
        setFile(null);
        setResult(null);
        setError('Choose a JPEG, PNG or WebP image.');
        return
      }
      if (nextFile.size > 10 * 1024 * 1024) {
        setFile(null);
        setResult(null);
        setError('The image must be smaller than 10 MB.');
        return
      }
      setFile(nextFile);
      setResult(null);
      setError('')
    }

    async function submit(event) {
      event.preventDefault()
      if (!file) {
        setError('Choose a photo to continue.');
        return
      }
      if (!selectedRegion) {
        setError(regions.length ? 'Choose a region to continue.' : 'Regions are unavailable. Check the classification service.');
        return
      }
      setBusy(true);
      setError('');
      setResult(null)
      try {
        setResult(await sendPhoto(file, selectedRegion))
      } catch (err) {
        setError(err.message)
      } finally {
        setBusy(false)
      }
    }

    const classification = result?.classification
    const notice = error || regionError
    return <main className={`page-content photo-page${result ? ' has-result' : ''}`}>
      <div className="section-heading"><span className="eyebrow">PHOTO IDENTIFICATION</span><p>Upload an item photo and
        choose your region.</p></div>
      <div className="photo-layout">
        <form className="panel upload-panel" onSubmit={submit}>
          <RegionSelect regions={regions} value={selectedRegion} onChange={chooseRegion}/>
          <div className={`drop-zone${dragging ? ' is-dragging' : ''}${preview ? ' has-preview' : ''}`}
               onDragOver={event => {
                 event.preventDefault();
                 setDragging(true)
               }}
               onDragLeave={event => {
                 event.preventDefault();
                 setDragging(false)
               }}
               onDrop={event => {
                 event.preventDefault();
                 setDragging(false);
                 chooseFile(event.dataTransfer?.files?.[0])
               }}>
            {preview ? <img className="photo-preview" src={preview} alt="Selected item"/> :
                <span className="upload-symbol"><Icon name="upload"/></span>}
            <strong>{file ? file.name : 'Drop a photo here'}</strong>
            <span
                className="desktop-drop-hint">{file ? 'Choose another if needed' : 'or choose a file from your device'}</span>
            <input ref={fileInput} type="file" accept="image/jpeg,image/png,image/webp" onChange={event => {
              chooseFile(event.target.files[0]);
              event.target.value = ''
            }} hidden/>
            <button type="button" className="secondary-button" onClick={() => fileInput.current?.click()}>Choose file
            </button>
          </div>
          <p className="helper-text">JPEG, PNG or WebP · up to 10 MB</p>
          <button className="primary-button wide" disabled={busy}>{busy ? 'Analyzing photo…' : 'Get recommendation'}
            <Icon name="arrow"/></button>
        </form>
        <section className="panel result-panel" aria-live="polite"><span className="panel-kicker">YOUR RESULT</span>
          {!result ?
              <div className={`empty-result${notice ? ' has-notice' : ''}`} role={notice ? 'alert' : undefined}><span
                  className="empty-result-icon"><Icon name={notice ? 'warning' : 'check'}/></span>
                <h2>{notice ? 'Check your selection' : 'Ready when you are'}</h2>
                <p>{notice || 'Choose a region and upload a photo to see your classification and disposal recommendation.'}</p>
              </div> : <>
                <h2>{result.status === 'ok' ? 'Disposal recommendation' : 'Please try another photo'}</h2>
                {classification && <div className="result-facts">
                  <div><span>Item</span><strong>{classification.waste_class || 'Unidentified'}</strong></div>
                  <div>
                    <span>Category</span><strong>{categories.find(item => item.key === result.category)?.label || result.category}</strong>
                  </div>
                </div>}
                <div className="instruction-box"><span>What to do</span><p>{result.message}</p></div>
                <p className="result-region">For {result.region}</p>
                <button className="secondary-button another-photo" onClick={() => {
                  setResult(null);
                  setFile(null)
                }}>Try another photo
                </button>
              </>}
        </section>
      </div>
      {notice && <p className="error-banner mobile-notice" role="alert">{notice}</p>}
    </main>
  }

  const CHAT_TOKEN_KEY = 'diligen-chat-token'
  const UUID_PATTERN = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i

  function loadChatToken() {
    try {
      const saved = sessionStorage.getItem(CHAT_TOKEN_KEY)
      if (saved && UUID_PATTERN.test(saved)) return saved
      const token = crypto.randomUUID()
      sessionStorage.setItem(CHAT_TOKEN_KEY, token)
      return token
    } catch {
      return crypto.randomUUID()
    }
  }

  function ChatPage() {
    const [token] = useState(loadChatToken)
    const [messages, setMessages] = useState([])
    const [text, setText] = useState('')
    const [loading, setLoading] = useState(true)
    const [busy, setBusy] = useState('')
    const [error, setError] = useState('')
    const bottom = useRef(null)
    useEffect(() => {
      bottom.current?.scrollIntoView({behavior: 'smooth'})
    }, [messages, busy])

    useEffect(() => {
      let active = true
      getChat(token).then(history => {
        if (active) setMessages(Array.isArray(history) ? history : [])
      })
          .catch(err => {
            if (active) setError(err.message)
          })
          .finally(() => {
            if (active) setLoading(false)
          })
      return () => {
        active = false
      }
    }, [token])

    async function submit(event) {
      event.preventDefault()
      const question = text.trim()
      if (!question || busy || loading) return
      setMessages(current => [...current, {role: 'user', content: question}]);
      setText('');
      setBusy('send');
      setError('')
      try {
        const reply = await sendChat(token, question)
        setMessages(current => [...current, reply])
      } catch (err) {
        setError(err.message)
      } finally {
        setBusy('')
      }
    }

    async function clear() {
      if (busy || loading) return
      setBusy('clear');
      setError('')
      try {
        await clearChat(token);
        setMessages([])
      } catch (err) {
        setError(err.message)
      } finally {
        setBusy('')
      }
    }

    return <main className="page-content chat-page">
      <div className="section-heading chat-heading">
        <div><span className="eyebrow">AI RECYCLING ASSISTANT</span><p>Ask a question and mention your region if local
          rules matter.</p></div>
        <button type="button" className="secondary-button" onClick={clear}
                disabled={!messages.length || Boolean(busy) || loading}><Icon name="trash"/> Clear chat
        </button>
      </div>
      <section className="panel chat-panel" aria-label="Chat with AI recycling assistant">
        <div className="chat-messages" aria-live="polite">
          <div className="chat-message assistant"><span className="message-avatar">D</span>
            <div className="message-bubble">Hello! Ask me how to sort an item. Please mention your city or region if
              local rules matter.
            </div>
          </div>
          {messages.map((message, index) => <div key={index}
                                                 className={`chat-message ${message.role === 'user' ? 'user' : 'assistant'}`}>
            {message.role !== 'user' && <span className="message-avatar">D</span>}
            <div className="message-bubble">{message.content}</div>
          </div>)}
          {loading && <div className="chat-message assistant"><span className="message-avatar">D</span>
            <div className="message-bubble muted">Loading your conversation…</div>
          </div>}
          {busy === 'send' && <div className="chat-message assistant"><span className="message-avatar">D</span>
            <div className="message-bubble muted">Thinking…</div>
          </div>}
          <div ref={bottom}/>
        </div>
        {error && <p className="chat-error" role="alert">{error}</p>}
        <form className="chat-form" onSubmit={submit}><label className="sr-only" htmlFor="question">Your
          question</label>
          <textarea id="question" value={text} onChange={event => setText(event.target.value)} maxLength={500} rows={2}
                    placeholder="For example: How do I dispose of a pizza box in Dortmund?" onKeyDown={event => {
            if (event.key === 'Enter' && !event.shiftKey) {
              event.preventDefault();
              event.currentTarget.form.requestSubmit()
            }
          }}/>
          <button className="send-button" type="submit" disabled={!text.trim() || Boolean(busy) || loading}
                  aria-label="Send message"><Icon name="send"/></button>
        </form>
      </section>
    </main>
  }

  function TrendLineChart({days}) {
    const width = Math.max(720, days.length * 70)
    const left = 42
    const right = width - 20
    const top = 18
    const bottom = 150
    const maximum = Math.max(1, ...days.flatMap(day => categories.map(category => day[`${category.key}_count`] || 0)))
    const points = days.map((day, index) => ({
      ...day,
      x: days.length === 1 ? (left + right) / 2 : left + index * (right - left) / (days.length - 1),
    }))

    return <>
      <div className="trend-chart">
        <svg width={width} height="190" viewBox={`0 0 ${width} 190`} role="img"
             aria-label="Daily classifications by category">
          {[0, 0.5, 1].map(level => {
            const y = bottom - level * (bottom - top)
            return <g key={level}>
              <line className="chart-grid-line" x1={left} x2={right} y1={y} y2={y}/>
              <text className="chart-axis-label" x={left - 10} y={y + 4}
                    textAnchor="end">{Math.round(maximum * level)}</text>
            </g>
          })}
          {categories.map(category => {
            const series = points.map(point => ({
              ...point,
              count: point[`${category.key}_count`] || 0,
              y: bottom - (point[`${category.key}_count`] || 0) / maximum * (bottom - top),
            }))
            return <g key={category.key}>
              <polyline className="chart-line" stroke={category.color}
                        points={series.map(point => `${point.x},${point.y}`).join(' ')}/>
              {series.map(point => <circle className="chart-point" key={point.period} cx={point.x} cy={point.y} r="4"
                                           stroke={category.color}>
                <title>{point.period}: {category.label} — {point.count}</title></circle>)}
            </g>
          })}
          {points.map(point => <text className="chart-axis-label" key={point.period} x={point.x} y="177"
                                     textAnchor="middle">{point.period.slice(5)}</text>)}
        </svg>
      </div>
      <div className="trend-legend" aria-label="Chart categories">{categories.map(category => <span
          key={category.key}><i style={{background: category.color}}/>{category.label}</span>)}</div>
    </>
  }

  function DashboardPage({ analyticsState }) {
    const {regions: storedRegions, error: regionError} = useRegions('/analytics/regions')
    const regions = ['__all__', ...storedRegions.filter(region => region !== '__all__')]
    const [region, setRegion] = useState('__all__')
    const [period, setPeriod] = useState('all')
    const [statistics, setStatistics] = useState(null)
    const [trends, setTrends] = useState([])
    const [live, setLive] = useState(false)
    const [refresh, setRefresh] = useState(0)
    const [busy, setBusy] = useState(false)
    const [error, setError] = useState('')
    const [updatedAt, setUpdatedAt] = useState(null)

    useEffect(() => {
      let active = true

      async function load() {
        setBusy(true)
        try {
          const encoded = encodeURIComponent(region)
          const query = period === 'all' ? '' : `?days=${period}`
          const [summary, daily] = await Promise.all([getJson(`/analytics/${encoded}/statistics${query}`), getJson(`/analytics/${encoded}/trends${query}`)])
          if (active) {
            setStatistics(summary);
            setTrends(daily);
            setUpdatedAt(new Date());
            setError('')
          }
        } catch (err) {
          if (active) setError(err.message)
        } finally {
          if (active) setBusy(false)
        }
      }

      load()
      const timer = live ? window.setInterval(load, 15000) : null
      return () => {
        active = false;
        if (timer) window.clearInterval(timer)
      }
    }, [region, period, live, refresh])

    const distribution = categories.map(item => ({...item, value: statistics?.[`${item.key}_percentage`] || 0}))
    const peakDay = trends.reduce((best, day) => {
  const total = categories.reduce(
    (sum, category) =>
      sum + (Number(day[`${category.key}_count`]) || 0),
    0
  );

  return total > best.total
    ? { total, period: day.period }
    : best;
}, { total: 0, period: null });

    const totalPercentage = distribution.reduce(
        (sum, item) => sum + item.value, 0
    )

    let currentPosition = 0

    const gradientStops = distribution.map(item => {
      const start = currentPosition
      currentPosition += totalPercentage
          ? (item.value / totalPercentage) * 100
          : 0

      return `${item.color} ${start}% ${currentPosition}%`
    }).join(', ')

    const donutBackground = totalPercentage
        ? `conic-gradient(${gradientStops})`
        : '#edf2ed'

    const analyticsStatusText = {
        ready: 'Connected',
        checking: 'Checking...',
        waking: 'Reconnecting...',
        down: 'Disconnected'
      }[analyticsState] || 'Checking...';

    return <main className="page-content dashboard-page">
      <div className="section-heading"><span className="eyebrow">WASTE ANALYTICS</span><p>Explore recorded
        classifications by region and category.</p></div>
      <div className="dashboard-toolbar panel">
        <div className="dashboard-filters"><RegionSelect regions={regions} value={region} onChange={setRegion}
                                                         showPlaceholder={false}/>
          <label className="field-label">Period<select value={period} onChange={event => setPeriod(event.target.value)}>
            <option value="7">Last 7 days</option>
            <option value="30">Last 30 days</option>
            <option value="all">All time</option>
          </select></label></div>
        <div className="dashboard-controls">
          <div
            className={`analytics-status analytics-status--${analyticsState}`}
            role="status"
          >
  <span className="analytics-status-dot" />
  Analytics: {analyticsStatusText}
</div>
          <label className="toggle-label"><input type="checkbox" checked={live}
                                                                                   onChange={event => setLive(event.target.checked)}/><span
            className="toggle-track"/><span>Auto refresh</span></label>
          <button className="secondary-button refresh-button" onClick={() => setRefresh(value => value + 1)}
                  disabled={busy}><Icon name="refresh"/> Refresh
          </button>
        </div>
      </div>
      <p className="updated-line">{busy ? 'Updating…' : updatedAt ? `Updated ${updatedAt.toLocaleTimeString()}` : 'Waiting for data'}{live && ' · Automatically refreshes every 15 seconds'}</p>
      {(error || regionError) && <p className="error-banner" role="alert">{error || regionError}</p>}
      <div className="dashboard-grid">
        <section className="panel summary-panel">
  <span className="panel-kicker">
    PEAK DAILY ACTIVITY
  </span>

  <strong className="big-number">
    {trends.length ? peakDay.total : '—'}
  </strong>

  <p>
    {peakDay.period
      ? `Highest daily activity on ${new Date(
          `${peakDay.period}T12:00:00`
        ).toLocaleDateString('en-GB', {
          day: 'numeric',
          month: 'short',
          year: 'numeric'
        })}`
      : 'No activity in the selected period'}
  </p>
</section>
        <section className="panel distribution-panel">

  <span className="panel-kicker">
    CATEGORY DISTRIBUTION
  </span>

          <h2>Where items go</h2>

          {statistics?.total_records > 0 ? (
              <div className="distribution-visual">

                <div
                    className="distribution-donut"
                    style={{background: donutBackground}}
                    role="img"
                    aria-label="Waste category distribution"
                >
                  <div className="donut-center">
                    <strong>{statistics.total_records}</strong>
                    <span>Items</span>
                  </div>
                </div>

                <div className="category-list">
                  {distribution.map(item => (
                      <div key={item.key}>
            <span>
              <i style={{background: item.color}}/>
              {item.label}
            </span>

                        <strong>{item.value.toFixed(1)}%</strong>
                      </div>
                  ))}
                </div>

              </div>
          ) : (
              <p className="no-data">
                No records for this region yet.
              </p>
          )}

        </section>
        <section className="panel trends-panel"><span className="panel-kicker">DAILY ACTIVITY</span><h2>Classification
          trend</h2>
          {trends.length ? <TrendLineChart days={trends}/> :
              <p className="no-data">No activity has been recorded yet.</p>}
        </section>
      </div>
    </main>
  }

  function useServiceStatus() {
    const [status, setStatus] = useState(() => Object.fromEntries(Object.keys(services).map(key => [key, {
      state: 'checking',
      everReady: false
    }])))
    const running = useRef({})
    const down = useRef({})
    const active = useRef(false)

    const check = useCallback(async (key, immediate = false) => {
      if (running.current[key]) return
      running.current[key] = true
      down.current[key] = false
      const update = state => setStatus(current => ({
        ...current,
        [key]: {state, everReady: current[key].everReady || state === 'ready'}
      }))
      if (immediate) update('waking')
      const slowTimer = setTimeout(() => {
        if (active.current) update('waking')
      }, 1500)
      const awake = await wakeService(services[key].url, () => !active.current)
      clearTimeout(slowTimer)
      running.current[key] = false
      if (!active.current) return
      down.current[key] = !awake
      update(awake ? 'ready' : 'down')
    }, [])

    useEffect(() => {
      active.current = true
      let lastCheck = 0
      const checkAll = () => {
        lastCheck = Date.now();
        Object.keys(services).filter(key => !down.current[key]).forEach(key => check(key))
      }
      const onVisible = () => {
        if (document.visibilityState === 'visible' && Date.now() - lastCheck > 60000) checkAll()
      }
      checkAll()
      const pingTimer = setInterval(() => {
        if (document.visibilityState === 'visible') checkAll()
      }, KEEP_AWAKE_MS)
      document.addEventListener('visibilitychange', onVisible)
      return () => {
        active.current = false
        clearInterval(pingTimer)
        document.removeEventListener('visibilitychange', onVisible)
      }
    }, [check])

    return [status, key => check(key, true)]
  }

  function ServiceGate({name, status, retry, children}) {
    const down = status.state === 'down'
    const notice = status.state === 'waking' || down ?
        <div className="panel service-notice" role="status" aria-live="polite">
          <span className="card-icon"><Icon name={down ? 'warning' : 'refresh'}/></span>
          <h2>{down ? `${name} isn't responding` : `${name} is starting…`}</h2>
          <p>{down ? 'The service may be offline. The other parts of the site still work.' : 'After a quiet period this can take up to a minute.'}</p>
          {down && <button type="button" className="secondary-button" onClick={retry}><Icon name="refresh"/> Try again
          </button>}
        </div> : null
    if (!status.everReady) return <main className="page-content service-wait">{notice}</main>
    const locked = status.state !== 'ready'
    return <>
      <div inert={locked} className="service-content">{children}</div>
      {locked && notice && <div className="service-overlay">{notice}</div>}
    </>
  }

  export default function App() {
    const [page, setPage] = useState('home')
    const [status, retry] = useServiceStatus()
    useEffect(() => {
      window.scrollTo(0, 0)
    }, [page])
    const key = pageService[page]
    const pages = {photo: <PhotoPage/>, chat: <ChatPage/>, dashboard: (
  <DashboardPage
    analyticsState={status.analytics?.state ?? 'checking'}
  />
)}
    return <div className={`app-shell${page === 'chat' ? ' chat-shell' : ''}`}>
      <Header
        page={page}
        goHome={() => setPage('home')}
    />
      {page === 'home'
          ? <Home setPage={setPage} status={status}/>
          : <ServiceGate key={page} name={services[key].name} status={status[key]}
                         retry={() => retry(key)}>{pages[page]}</ServiceGate>}
      <footer className="site-footer">Diligen <span>·</span> Smarter waste sorting</footer>
    </div>
  }
