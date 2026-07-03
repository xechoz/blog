// 极简主题覆盖：替换主题的 index 和 post 模板
// 不修改 themes/cactus 下的任何文件

const indexTemplate = `
<!-- 极简主页：纯文章列表，按时间倒序 -->
<section id="writing">
  <ul class="post-list">
    <% page.posts.sort('date', 'desc').each(function(post){ %>
      <li class="post-item">
        <time class="meta" datetime="<%= date_xml(post.date) %>">
          <%- date(post.date, 'YYYY-MM-DD') %>
        </time>
        <a href="<%- url_for(post.path) %>"><%= post.title %></a>
      </li>
    <% }); %>
  </ul>
  <%- partial('_partial/pagination') %>
</section>
`;

const postTemplate = `
<!-- 极简文章详情页：标题 + 日期 + 正文 -->
<article class="post h-entry" itemscope itemtype="http://schema.org/BlogPosting">
  <header>
    <%- partial('_partial/post/title', { post: page, index: false, class_name: 'posttitle' }) %>
    <div class="meta">
      <%- partial('_partial/post/date', { post: page, class_name: 'postdate' }) %>
    </div>
  </header>
  <div class="content e-content" itemprop="articleBody">
    <%- page.content %>
  </div>
</article>
`;

// 在生成之前，用自定义模板替换主题的 index 和 post 视图
hexo.extend.filter.register('before_generate', function () {
    const theme = hexo.theme;

    // 替换 index.ejs
    theme.setView('index', indexTemplate);

    // 替换 post.ejs
    theme.setView('post', postTemplate);

    // 也处理带后缀的情况
    theme.setView('index.ejs', indexTemplate);
    theme.setView('post.ejs', postTemplate);
});
