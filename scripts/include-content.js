const fs = require('fs')
const path = require('path')

hexo.extend.filter.register('before_post_render', function (data) {
  data.content = data.content.replace(/\{% include_content (.+?) %\}/g, (_, filename) => {
    const source = data.full_source
    const assetDir = source.replace(/\.md$/, '')
    const file = path.join(assetDir, filename.trim())

    if (fs.existsSync(file)) {
      return fs.readFileSync(file, 'utf8')
    }

    hexo.log.warn(`include_content: file not found: ${filename} (looked in ${assetDir})`)
    return ''
  })

  return data
})
