
function trimSpaces(s) {
    return s.replaceAll("\n", "").replace(/\s+/g, ' ').trim();
}
const cmts = $("shreddit-comment")
const out = []
// Parse comments from html
cmts.each((i, cmt) => {
    const $cmt = $(cmt)
    // Author: slot="commentMeta" (use the first one)
    const author = trimSpaces($cmt.find("[slot=commentMeta]").first().text())
    // Content: slot="comment"
    const content = trimSpaces($cmt.find("[slot=comment]").first().text())
    // Upvotes: score attribute of shreddit-comment-action-row
    const upvotes = parseInt($cmt.find("shreddit-comment-action-row").attr("score"))
    out.push({ author, content, upvotes })
})
out